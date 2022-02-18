import json
import pulumi_aws as aws


#Environment variable file
with open("./../config.json") as config_file:
    data = json.load(config_file)


ENV = "prod"    
ENV_ACCOUNT = data['ACCOUNT'][ENV.upper()]['ID']
SHAREDBACKUPS_ACCOUNT = data["ACCOUNT"]["SHAREDBACKUPS"]["ID"]
SHAREDBACKUPS_KEY = data["ACCOUNT"]["SHAREDBACKUPS"]["KMS"]
REGION = data["REGION"]
IAM_USER = data["IAM_USER"]


# opting in aws service for AWS backup
service_opt_in = aws.backup.RegionSettings(
    "service-opt-in",
    resource_type_opt_in_preference={
        "Aurora": True,
        "DynamoDB": True,
        "EBS": True,
        "EC2": True,
        "EFS": True,
        "FSx": True,
        "RDS": True,
        "Storage Gateway": True,
    },
)

# creating backup service role

backups_service_role = aws.iam.Role(
    f"backups-service-role",
    name=f"backups-service-role",
    assume_role_policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Effect": "Allow",
                    "Sid": "",
                    "Principal": {
                        "Service": "backup.amazonaws.com",
                    },
                }
            ],
        }
    ),
    managed_policy_arns=[
        "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForBackup",
        "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForRestores",
    ],
    tags={
        "ENVIRONMENT": ENV,
        "Name": f"backups-service-role-{ENV}",
        "BUSINESS_UNIT": "Security",
        "SUPPORT_EMAIL": "abc@xyz.com",
        "PRIVACY": "high",
    },
)

# creating backup vault

backups_vault = aws.backup.Vault(
    f"backups-vault-prod",
    name=f"backups-vault-prod",
    kms_key_arn=f"arn:aws:kms:{REGION}:{SHAREDBACKUPS_ACCOUNT}:key/{SHAREDBACKUPS_KEY}",
    tags={
        "ENVIRONMENT": ENV,
        "Name": f"backups-vault-nonprod",
        "BUSINESS_UNIT": "Security",
        "SUPPORT_EMAIL": "abc@xyz.com",
        "PRIVACY": "high",
    },
)

# creating backup vault policy to allow sharedbackups account access to the vault

backups_vault_policy = aws.backup.VaultPolicy(
    f"backups-vault-policy-{ENV}",
    backup_vault_name=backups_vault.name,
    policy=backups_vault.arn.apply(
        lambda arn: f"""{{
  "Version": "2012-10-17",
  "Id": "default",
  "Statement": [
    {{
      "Sid": "default",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "backup:CopyIntoBackupVault",
      "Resource": "*",
      "Principal": {{
          "AWS": [
                    "arn:aws:iam::{SHAREDBACKUPS_ACCOUNT}:root"
                ]
      }}
    }}
  ]
}}
"""
    ),
)