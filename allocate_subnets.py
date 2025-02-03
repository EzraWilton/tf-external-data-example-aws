import ipaddress
import json
import sys
import yaml

def merge_contiguous_blocks(blocks):
    """
    Merge contiguous IP blocks into the largest possible subnet.
    """
    blocks = sorted(blocks, key=lambda x: x.network_address)
    merged_blocks = []

    for block in blocks:
        if merged_blocks and merged_blocks[-1].supernet_of(block):
            merged_blocks[-1] = merged_blocks[-1].supernet()
        else:
            merged_blocks.append(block)

    return merged_blocks


def allocate_subnets(vpc_cidr, subnet_requests):
    """
    Allocate subnets hierarchically within a given VPC CIDR, ensuring efficient space usage.

    :param vpc_cidr: The base CIDR block of the VPC.
    :param subnet_requests: List of subnet requests as (name, mask, override_cidr).
    :return: Dictionary of allocated subnets with their CIDRs.
    """
    vpc_network = ipaddress.IPv4Network(vpc_cidr, strict=False)
    allocated_subnets = {}
    allocated_subnets_blocks = {}
    available_blocks = [vpc_network]  # Start with the full VPC block

    for name, mask, override_cidr in sorted(subnet_requests, key=lambda x: x[1]):
        if override_cidr:
            subnet = ipaddress.IPv4Network(override_cidr, strict=False)
        else:
            subnet = None
            available_blocks.sort(key=lambda x: x.network_address)  # Ensure blocks are allocated in order
            for i, block in enumerate(available_blocks):
                if block.prefixlen < mask:  # Ensure we can split this block
                    for candidate in block.subnets(new_prefix=mask):
                        subnet = candidate
                        available_blocks.pop(i)
                        available_blocks.extend(block.address_exclude(subnet))
                        break
                if subnet:
                    break

        if subnet is None:
            continue

        allocated_subnets[name] = str(subnet)  # Store only CIDR as a string
        allocated_subnets_blocks[name] = subnet

    contiguous_blocks = []
    fragmented_blocks = []
    allocated_networks = list(allocated_subnets_blocks.values())

    for block in sorted(available_blocks, key=lambda x: x.network_address):
        overlaps = any(block.overlaps(allocated) for allocated in allocated_networks)
        fully_contained = any(allocated.supernet_of(block) for allocated in allocated_networks)

        if overlaps and not fully_contained:
            fragmented_blocks.append(block)  # Mid-block free space (yellow in diagram)
        elif not overlaps:
            contiguous_blocks.append(block)  # Unused top-level blocks (blue in diagram)

    # Merge contiguous free blocks
    contiguous_blocks = merge_contiguous_blocks(contiguous_blocks)


    return allocated_subnets, contiguous_blocks


if __name__ == "__main__":
    terraform_input = json.loads(sys.stdin.read())
    config_file = terraform_input.get("config_file", "config.yaml")

    with open(config_file, "r") as file:
        config = yaml.safe_load(file)

    vpc_cidr = list(config["NetworkDefinition"]["Networks"].keys())[0]
    subnet_requests = [
        (name, int(subnet["Mask"]), subnet.get("CidrOverride", None))
        for name, subnet in config["NetworkDefinition"]["Networks"][vpc_cidr]["Subnets"].items()
    ]

    allocated_subnets, free_subnets = allocate_subnets(vpc_cidr, subnet_requests)

    # Terraform requires a flat map with string values
    output = {
        "subnets": json.dumps(allocated_subnets),
        "free_subnets": json.dumps([str(block) for block in free_subnets]),
    }

    print(json.dumps(output))
