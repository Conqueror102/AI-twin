project_name             = "twin"
environment              = "prod"
# openai_api_key: set via TF_VAR_openai_api_key or terraform apply -var="openai_api_key=..." (do not commit)
openai_model             = "gpt-4o-mini"
lambda_timeout           = 60
api_throttle_burst_limit = 20
api_throttle_rate_limit  = 10
use_custom_domain        = true
root_domain              = "yourdomain.com"  # Replace with your actual domain