

// -------------- Network Alloc Logic----------------

// allocate_subnets.py
data "external" "subnet_allocator" {
  program = ["python", "${path.module}/allocate_subnets.py"]
  query = {
    config_file = "${path.module}/config.yaml"
  }
}

// config.yaml
data "local_file" "config" {
  filename = "${path.module}/config.yaml"
}


locals {
  config_data    = yamldecode(data.local_file.config.content)
  python_subnets = jsondecode(data.external.subnet_allocator.result["subnets"])
  python_subnets_free = jsondecode(data.external.subnet_allocator.result["free_subnets"])
  test_cidr = keys(local.config_data["NetworkDefinition"]["Networks"])[0]
  merged_subnets = {
    for name, subnet in local.config_data["NetworkDefinition"]["Networks"][local.test_cidr]["Subnets"] :
    name => merge(subnet, { "Cidr" = lookup(local.python_subnets, name, null) })
  }
}

output "allocated_subnets" {
  value = local.merged_subnets
}

output "free_subnets" {
  value = local.python_subnets_free
}
