# Claude Code Action — Cloud Provider Authentication

> Source: https://github.com/anthropics/claude-code-action/blob/main/docs/cloud-providers.md
> Fetched: 2026-02-11

## 1. Direct Anthropic API (Default)

```yaml
- uses: anthropics/claude-code-action@v1
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

## 2. AWS Bedrock (OIDC)

```yaml
- name: Configure AWS Credentials (OIDC)
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ secrets.AWS_ROLE_TO_ASSUME }}
    aws-region: us-west-2

- uses: anthropics/claude-code-action@v1
  with:
    use_bedrock: "true"
    claude_args: |
      --model anthropic.claude-4-0-sonnet-20250805-v1:0

permissions:
  id-token: write  # Required for OIDC
```

## 3. Google Vertex AI (OIDC)

```yaml
- name: Authenticate to Google Cloud
  uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: ${{ secrets.GCP_WORKLOAD_IDENTITY_PROVIDER }}
    service_account: ${{ secrets.GCP_SERVICE_ACCOUNT }}

- uses: anthropics/claude-code-action@v1
  with:
    use_vertex: "true"
    claude_args: |
      --model claude-4-0-sonnet@20250805
```

## 4. Microsoft Foundry / Azure (OIDC)

```yaml
- name: Authenticate to Azure
  uses: azure/login@v2
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

- uses: anthropics/claude-code-action@v1
  with:
    use_foundry: "true"
    claude_args: |
      --model claude-sonnet-4-5
  env:
    ANTHROPIC_FOUNDRY_BASE_URL: https://my-resource.services.ai.azure.com
```

## Notes

- No Claude Max/Pro subscription support via official action (API keys or cloud OIDC only)
- For subscription-based OAuth, see the community fork: grll/claude-code-action@beta
- All cloud providers use OIDC — no long-lived credentials stored
