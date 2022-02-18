import pulumi_aws as aws
import json



# config.json provides global and local variables
with open("./../../../config.json") as config_file:
    data = json.load(config_file)

ENV = "prod"
PROD_OU_ID = data["OU"]["PROD_OU_ID"]
SHAREDBACKUPS_ACCOUNT = data["ACCOUNT"]["SHAREDBACKUPS"]["ID"]
REGION = data["REGION"]

backups_policy_prod = aws.organizations.Policy(
    f"backups-policy-{ENV}",
    name=f"backups-policy-{ENV}",
    description="backups policy for prod ENVironment",
    type="BACKUP_POLICY",
    content=f"""{{
    "plans": {{
        "backups-policy-prod-plan": {{
            "regions": {{
                "@@assign": [
                    "{REGION}"
                ]
            }},
            "rules": {{
                "backups-policy-prod-rule": {{
                    "schedule_expression": {{
                        "@@assign": "cron(00 16 ? * * *)"
                    }},
                    "start_backup_window_minutes": {{
                        "@@assign": "60"
                    }},
                    "complete_backup_window_minutes": {{
                        "@@assign": "120"
                    }},
                    "lifecycle": {{
                        "delete_after_days": {{
                            "@@assign": "28"
                        }}
                    }},
                    "target_backup_vault_name": {{
                        "@@assign": "backups-vault-prod"
                    }},
                    "copy_actions": {{
                        "arn:aws:backup:{REGION}:{SHAREDBACKUPS_ACCOUNT}:backup-vault:sharedbackups-vault-prod": {{
                            "target_backup_vault_arn": {{
                                "@@assign": "arn:aws:backup:{REGION}:{SHAREDBACKUPS_ACCOUNT}:backup-vault:sharedbackups-vault-prod"
                            }},
                            "lifecycle": {{
                                "delete_after_days": {{
                                    "@@assign": "730"
                                }},
                                "move_to_cold_storage_after_days": {{
                                    "@@assign": "30"
                                }}
                            }}
                        }}
                    }}
                }}
            }},
            "selections": {{
                "tags": {{
                    "rds": {{
                        "iam_role_arn": {{
                            "@@assign": "arn:aws:iam::$account:role/backups-service-role"
                        }},
                        "tag_key": {{
                            "@@assign": "Backup"
                        }},
                        "tag_value": {{
                            "@@assign": [
                                "yes"
                            ]
                        }}
                    }}
                }}
            }}
        }}
    }}
}}

""",
)

backups_policy_prod_attachment = aws.organizations.PolicyAttachment(
    "backups-policy-prod-attachment",
    policy_id=backups_policy_prod.id,
    target_id=PROD_OU_ID,
)
