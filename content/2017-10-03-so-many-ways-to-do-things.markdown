Title: So Many Ways to Do Things
Date: 2017-10-03
Tags: linux,cli,packages,slick
Category: blog

I've been using the Archlinux User Repository (AUR) to occaisonally grab some less-than-primetime packages.  It's basically a `git clone` command followed by `makepkg` and `sudo pacman -U [package_tarball]`.  Not so bad, but I figured why don't I at least speed up the git-ing.

I found [this](https://stackoverflow.com/questions/4438147/alias-with-variable-in-bash) on stackoverflow which details how to write a function in your .bashrc that does some argument substitution, ala:

```
function gitaur { git clone https://aur.archlinux.org/"$1"; }
export -f gitaur
```

Pretty sweet.  Just type `gitaur dokku`, for example.

But then I discovered [`yaourt`](https://archlinux.fr/man/yaourt.8.html).  It's suggested right on dokku's [installation page](http://dokku.viewdocs.io/dokku/#install-arch).  It's a pacman frontend that pulls from both official Archlinux repositories and the AUR, spits out comments related to AUR packages, warns you profusely, and even lets you edit installation config files along the way.

So much for my fancy function.  At least I got to use it to clone yaourt from the AUR. ;)
