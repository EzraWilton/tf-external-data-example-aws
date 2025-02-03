<h1>Terraform External Data example - Passing CIDR calculations to python</h1>
This example shows how to pass data from terraform to python, and then back to terraform do to additional calculations
which may prove difficult in terraform or produce hard-to-maintain code. A good example of this is efficient CIDR
allocation, which is a common problem in cloud deployments and hard to implement natively in Terraform. 

<h4> Note - Python requirements:  </h4>
Terraform data object is invoking python based on system it runs on - for local runs, tweak this to your local 
environment's commands

Python also requires a few modules, see requirements.txt