Title:  Abstracting Secrets from Terraform Files
Date: 2018-02-28
Tags: secrets,terraform,tf,agent,ssh,ssh-agent,ssh-add,bashrc
Category: blog

It's no secret that secrets should be kept away from baddies, but maybe more insidious is the accidental divulging of secrets through hard coded values, git pushes or pasting code into blogs.  Humans are after all the weakest link in security.

Terraform is a tool that by nature needs access to many of your secrets:  

* Cloud provider credentials for API connections
* SSH private keys for connecting to remote hosts 

I'd like to share a method to help prevent those accidental spills through the vector of your `.tf` files.

### Cloud Provider Creds in Environment Variables

Each cloud provider you do business with will supply you with API keys and secrets that you, or some unsavory individual, can use to build out intricate masterpieces in the cloud... and potentially rack up quite the bill.  The provider constructs in Terraform give you a multitude of ways to set these credentials:

**Through the provider variables directly.**  This method is most likely of the three to result in accidental sharing of secrets, namely when you share your code.
```
provider "aws" {
    region     = "us-west-2"
    access_key = "anaccesskey"
    secret_key = "asecretkey"
}
```

**Or provider variables pointing to files.**  This is more robust.  Though not all Terraform providers have this property, you can put the key strings into individual files and use `"${file(chomp(accesskey.file))}"` to the same effect.
```
provider "aws" {
    region                  = "us-west-2"
    shared_credentials_file = "/Users/tf_user/.aws/creds"
    profile                 = "customprofile"
}
```

**Or through environment variables.**  No sign of credentials or even their location on your local machine are visible in any of your Terraform code.  While a bit inconvenient it is certainly much DRY-er than the above, and there are several ways to make this as easy.
```
$ export AWS_ACCESS_KEY_ID="anaccesskey"
$ export AWS_SECRET_ACCESS_KEY="asecretkey"
$ export AWS_DEFAULT_REGION="us-west-2"
$ terraform plan
```

Some people have a bash script that runs `terraform apply` and maybe a separate one to `terraform destroy`.  In those scripts you can export the environment variables as above and run along blithely.  However this still leaves values hard-coded into your scripts which typically sit in the same directory (eg, git repo) as your `.tf` files.  You might opt to have those scripts `export KEY=$(cat ~/credsfile.key)` to avoid hardcoding but that's not DRY.  Nevertheless this might be the most workable solution if you are dealing with several accounts for a given cloud provider.

I opt to export my environment variables in my `.bashrc` init file, indirectly.

_.bashrc_
```
# this sources the definition file for my 
# cloud provider environment variables
source /path/to/env-var-export
```

_env-var-export_
```
# here's where the real secrets lie
export DIGITALOCEAN_TOKEN="long-token-string"

export AWS_ACCESS_KEY_ID="shorter-access-key"
export AWS_SECRET_ACCESS_KEY="longer-secret-access-key"

export GOOGLE_APPLICATION_CREDENTIALS="/path/to/gcloud/credentials.json"
```

Using the latter two methods your Terraform provider definitions look much cleaner, almost like an `import` or `include` statement.
```
provider "digitalocean" {}
```

In my next blog post I'll go over using `ssh-agent` to remove the need to supply your ssh private file to Terraform through your `.tf` files.

* * *
