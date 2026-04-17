project_name             = "twin"
environment              = "dev"
# openai_api_key: set via TF_VAR_openai_api_key or terraform apply -var="openai_api_key=..."
openai_model             = "gpt-4o-mini"
lambda_timeout           = 60
api_throttle_burst_limit = 10
api_throttle_rate_limit  = 5
use_custom_domain        = false
root_domain              = ""