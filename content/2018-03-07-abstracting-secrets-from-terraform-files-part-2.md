Title:  Abstracting Secrets from Terraform Files - Part 2
Date: 2018-03-07
Tags: secrets,terraform,tf,agent,ssh,ssh-agent,ssh-add,bashrc,vim,argdo
Category: blog

In the [last post][] I broached the subject of protecting your credentials from accidental spillage into the ecosystem through these vectors when using Terraform.

* Cloud provider credentials for API connections
* SSH private keys for connecting to remote hosts 

Today I'll share how to remove explicit references to your SSH private key(s) in `.tf` files.

### SSH Private Keys and SSH-Agent

I used to have this type of construct in my Terraform definition files:
```
resource "aws_instance" "box1" {
  ami           = "${data.aws_ami.ubuntu.id}"
  instance_type = "t2.micro"

  connection {
    type        = "ssh"
    private_key = "${file("/path/to/id_rsa")}"
  }

  provisioner "file" {
    source      = "/path/to/local/file"
    destination = "/path/to/remote/file"
  }
}
```

_For brevity I have minimal instance specification for the AWS instance._

Bring your focus to the `connection` block, namely the `private_key` property.  The connection block tells Terraform to authenticate an SSH connection to `box1` using the specified private key file.  This permits configuration of the host through [provisioners][].  Here the configuration phase consists of a sole `file` provisioner that copies a file from the local system to `box1`.  This is not a bad way to go, but let's explore the options and see if there's something better.

So what are the ways to securely connect to your hosts for Terraform administration?

**Secure your server with a password and specify the `password`.**  However there are [several advantages][] to using ssh public key authentication over password authentication.  Number 1 for me is automation:  I don't have to sit by and watch for a password prompt in my Terraforom rollout and try to sneak it in there (b/c I'm not hard coding my password!).  Number 2 is that to smooth out automation you have to hard code your password in your config files.  And that's a no-no.
```
  connection {
    type     = "ssh"
    password = "hard-coded-passwords-are-the-devil"
  }
```

**Secure your server with public key auth and use `private_key` to supply your private key data.**  You may supply credentials for the SSH connection via `private_key` by pasting your private key into your `.tf` files, in place or as a variable.  **Don't do this.**  There is a near 100% risk that if you share your code publicly your private key will be compromised.  That can have serious implications, even if you [rotate your keys][] frequently.
```
  connection {
    type        = "ssh"
    private_key = "sure-hope-you-aren't-putting-your-private-key-contents-here...
                   or-even-in-a-variable-declaration-elsewhere"
  }
```

**Secure your server with public key auth and use `private_key` to read the contents of your private key file.**  An acceptable way to supply a `private_key` is to use the `file` function to read from your local machine.  The Terraform suggests using the file function like so when employing the `private_key` property.
```
  connection {
    type        = "ssh"
    private_key = "${file("/path/to/id_rsa")}"
  }
```

This is a relatively secure method, and can be proofed by putting your private key path in a variable, referencing the variable in the connection block `private_key`, and adding the variable definition file to your `.gitignore` file.  Unless you clobber your .gitignore you won't even share the key's location.

_main.tf_
```
variable pri_key_file {}

...content omitted...

  connection {
    type        = "ssh"
    private_key = "${file(var.pri_key_file)}"
  }
```

_terraform.tfvars_
```
pri_key_file = "/path/to/id_rsa"
```

_.gitignore_
```
*.tfvars
```

Good, you're using public key authentication securely.  Yet the upper hand that public key auth has in terms of security is diminished if you don't protect your keys with a passphrase.  And here's the kicker:  Terraform's implementation of ssh does not support encrypted keys. 
```
*Failed to read key "-----BEGIN RSA PRIVATE KEY-----
...
-----END RSA PRIVATE KEY-----":  password protected keys are not supported. Please decrypt the key prior to use.
```
### SSH-Agent

There is yet another way enable SSH while keeping your private key squirreled away:  [ssh-agent][].

IMHO, ssh-agent is the pinnacle of secure, locally-based, Terraform-compatible public key authentication solutions.  If you are unfamiliar with ssh-agent, you can read more about it in the link above.  It functions as a broker for your ssh private keys by loading them into memory and cycling through them when making a public key authentication connection via any ssh-based.  If one of your loaded keys jives with the public key on the remote host you get a successful connection.

Get it started:
```
$ eval `ssh-agent`

Agent pid 24770
```

This command starts the ssh-agent process and exports two environment variables, `SSH_AUTH_SOCK` and `SSH_AGENT_PID`, which are used by ssh to connect with the agent.  Note that the pid is reported upon execution.

```
$ ssh-add [optional path to keys]

Identity added: /path/to/.ssh/id_rsa (/path/to/.ssh/id_rsa)
```

This command will automatically import keys with the names [`id_rsa`, `id_dsa`, `id_icdsa`, `id_ed25519`] from the default path of `~/.ssh/` .  Files appended as arguments will be pulled in as well.  You will be prompted for the passphrases for any protected keys import import.

Now for the fun part.

Remove all of the `private_keys` from your `.tf` connection blocks and erase any references to private key data.  Since ssh-agent is enabled by default you can now run `terraform apply`.

```
null_resource.test (remote-exec): Connecting to remote host via SSH...
null_resource.test (remote-exec):   Host: 123.45.67.89
null_resource.test (remote-exec):   User: youruser
null_resource.test (remote-exec):   Password: false
null_resource.test (remote-exec):   Private key: true
null_resource.test (remote-exec):   SSH Agent: true
null_resource.test (remote-exec): Connected!
```

This post is just meant as an introduction.  You should check out how to manage and select [ssh identities][] within Terraform.

And it's worth noting there are many [opinions][] on how to facilitate the [startup][] of `ssh-agent`.
* * *
[last post]:            {filename}/2018-02-28-abstracting-secrets-from-terraform-files.md
[provisioners]:         https://www.terraform.io/docs/provisioners/index.html
[ssh-agent]:            https://www.ssh.com/ssh/agent
[several advantages]:   https://www.ssh.com/manuals/server-zos-product/55/ch06s02s02.html   
[rotate your keys]:     https://hackernoon.com/ssh-key-rotation-b0877fbd75c2
[ssh identities]:       https://www.terraform.io/docs/provisioners/connection.html
[opinions]:             http://rabexc.org/posts/pitfalls-of-ssh-agents
[startup]:              https://stackoverflow.com/questions/18880024/start-ssh-agent-on-login 
