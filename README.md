<h1>Terraform External Data example - Passing CIDR calculations to python</h1>
This example shows how to pass data from terraform to python, and then back to terraform do to additional calculations
which may prove difficult in terraform or produce hard-to-maintain code. A good example of this is efficient CIDR
allocation, which is a common problem in cloud deployments and hard to implement natively in Terraform. 

<h2> Config.yaml </h2>
Config.yaml is intended as a higher level config file to define your network elements, i.e. for AWS.
For the purposes of this demo, only the CIDR and Subnet mask are used and returned back from the data element. This
is intended to be a pre-calcuation step to then pass to terraform for resource deployment. 

<h4> Note - Python requirements:  </h4>
Terraform data object is invoking python based on system it runs on - for local runs, tweak this to your local 
environment's commands

Python also requires a few modules, see requirements.txt

<h2> Usage </h2>
Clone this, run terraform init and then terraform plan. An output of the calculated CIDRs will be returned. 