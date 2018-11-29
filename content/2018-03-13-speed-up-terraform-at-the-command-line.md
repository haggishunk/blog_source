Title:  Speed Up Terraform at the Command Line
Date: 2018-03-13
Tags: terraform,tf,workspace,bash,dev,test,prod
Category: blog

We all want to save ourselves keystrokes.  And we should all want to have our Terraform projects divided into workspaces.  And if you are using workspaces, you might as well get a little statusline or command prompt info about which one you're currently working in.  I'd like to share a couple bash aliases & functions that collaborate with your command prompt and the terraform binary to make your deployments that much faster and easier.

It starts with using workspaces.  If you execute this command you will see what Terraform workspaces exist in the current working directory.
```
$ terraform workspace list

* default
```

If you haven't created any workspaces you will see the `default` one by default.

Create a new space.  Terraform will automatically activate this new space.
```
$ terraform workspace new dev

Created and switched to workspace "dev"!

You're now on a new, empty workspace. Workspaces isolate their state,
so if you run "terraform plan" Terraform will not see any existing state
for this configuration.
```

So when you have a couple workspaces, you might as well know which one you're in.  Try this function out in your `.bashrc` or equivalent.
```
function terraform-workspace {
    terraform workspace list 2>/dev/null | sed -e '/^[^*]/d' -e '/default/d' -e 's/* \(.*\)/ [\1]/'
}
```

This function handily extracts the active workspace text from the `terraform workspace list` command output, returning a non-`default` workspace name surrounded by brackets or an empty string.  Since _every_ directory on your machine has a `default` workspace (this is not part of `terraform init`), and since you ought to use non-default workspaces, I opted to eliminate `default`.

Now plug this into your PS1 command prompt.
```
PS1="[\u@\h \A \W\$(terraform-workspace)]\$ "
```

And you'll get a prompt like this in your Terraform workspace-active directories.  In this case the `dev` workspace is active. 
```
[user@home [dev]]$
```

Let's take it a step further with terraform's option to specify a variable file: `-var-file [some.tfvars]`.
```
function tp {
    terraform plan -var-file "$(terraform-workspace | tr -d "[ ]").tfvars" -out plan $@
}
```

This function transforms a very long sequence of keystrokes 
```
[user@home [dev]]$ terraform plan -var-file dev.tfvars -out plan ...
```

into two.
```
[user@home [dev]]$ tp ...
```

The design of this function requires you to use a variable file with a basename that matches the active workspace.  The above illustration highlights `dev`.

It is also built to output a plan called `plan`.  This works for me, but of course you can take it or leave it.
* * *
