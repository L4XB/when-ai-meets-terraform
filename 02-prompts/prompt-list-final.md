# Final Prompt List

## Easy (E1-E3)
E1: "Create a single EC2 t3.micro instance with SSH security group allowing access from anywhere in us-east-1 region"

E2: "Create an S3 bucket with a globally unique name, enable versioning, and create a bucket policy allowing read-only access"

E3: "Create a VPC with CIDR 10.0.0.0/16, one public subnet 10.0.1.0/24, and an internet gateway with proper routing"

## Medium (M1-M4)
M1: "Create a VPC with public subnet (10.0.1.0/24) and private subnet (10.0.2.0/24), including NAT gateway for private subnet internet access"

M2: "Create an Application Load Balancer in public subnets with 2 EC2 t3.micro instances as targets, including proper security groups"

M3: "Create RDS MySQL database instance in private subnets with Multi-AZ deployment and appropriate security group configuration"

M4: "Create Auto Scaling Group with minimum 2, maximum 4 EC2 instances behind an Application Load Balancer with health checks"

## Complex (C1-C4)
C1: "Create complete 3-tier architecture: Application Load Balancer + web tier (2 EC2 instances) + application tier (2 EC2 instances) + RDS MySQL database, all with proper security groups"

C2: "Create EKS cluster with managed node group using t3.medium instances, including all required IAM roles, policies, and security groups"

C3: "Create monitoring infrastructure with CloudWatch log groups, SNS topic for alerts, CloudWatch alarm for high CPU usage, and Lambda function for alert processing"

C4: "Create cross-region backup solution with S3 bucket, cross-region replication, automated EBS snapshots, and lifecycle policies"