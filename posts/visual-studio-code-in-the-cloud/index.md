---
date: "2022-09-28"
layout: post
title: Visual Studio Code on the Cloud
categories: [code, research, cloud]
---

Visual Studio Code is incredibly powerful, whether it's for writing [markdown](https://aeturrell.github.io/coding-for-economists/wrkflow-markdown.html), writing [quarto](https://aeturrell.github.io/coding-for-economists/wrkflow-quarto.html) (.qmd) files, getting syntax highlighting and peerless language support (eg auto-completion), getting peerless git support, working with a [co-pilot](https://github.com/features/copilot), [working with collaborators in real-time](https://visualstudio.microsoft.com/services/live-share/), or even running [R code in a modern REPL](http://aeturrell.com//2021/11/04/setting-up-r-in-vscode/). For me, it's the best IDE by some way. One of its strongest features for data science is its ability to do interactive window coding with scripts *and* notebooks. Yet most online or cloud-based data science services focus only on notebooks. Wouldn't it be great if there was a reliable way to use all of Visual Studio Code's features in the cloud?[^1]

[^1]: If you have a GitHub account you can just press '.' on a repo and it will load up something that looks a lot like Visual Studio Code but this can't run code, it's only a text editor.

In this blog post, I'll show you how to set up Visual Studio Code on your desktop so that it connects remotely to a cloud virtual machine. This will allow you to code on the cloud as if you were developing locally.[^caveats]

[^caveats]: We'll be using Google Cloud Compute but the concepts will be similar for other cloud services. You should also note that using cloud services is usually charged though free credits are often available for new accounts. Also, this has only been tested on MacOS.

Why should you care? Because having a reproducible environment on the cloud that you can use with your cutting-edge tools is pretty nifty!

There are pre-made resources out there that do this already such as [Github Codespaces](https://github.com/features/codespaces) and [Gitpod](https://www.gitpod.io/), which even has a free tier. They are incredible and well worth checking out for, more or less, a one click solution for fully-featued Visual Studio Code in the cloud. But they're probably a bit more pricey than a roll your own version, clearly have less flexibility in terms of virtual machines, and don't come with the nice data backends that are provided by a huge cloud provider (yet).

## Interactive Window Coding

If you're not familiar with it, the *interactive window*[^2] is a convenient and flexible way to run code that you have open in a script or that you type directly into the interactive window code box. It allows you to remix, explore, and try out code one line at a time or in chunks or as a whole script--which makes it perfect for analysis and data science on those occassions when you don't need text alongside code. You can find out more about [how to set up interactive window coding in Python with Visual Studio Code here](https://aeturrell.github.io/python4DS/introduction.html#installing-visual-studio-code-to-run-python) (and R [here](http://aeturrell.com//2021/11/04/setting-up-r-in-vscode/)). More generally, Visual Studio Code is a fantastic environment for doing data science in and many of its features eventually got adopted by other tools.

[^2]: This is actually a special kind of ipython console.

![Typical layout of Visual Studio Code](https://github.com/aeturrell/coding-for-economists/blob/main/img/vscode_layout.png?raw=true)

The figure above shows the typical layout of Visual Studio Code. Number 5 is the interactive Python window, which is where code and code outputs appear after you select and execute them from a script (number 3) or just by writing in the box 'Type code here' box.

## Setting Up

There are two pieces to this puzzle: Visual Studio Code and Google Cloud.

First, grab Visual Studio Code for your local computer (ie your non-cloud computer) and whatever extensions you fancy, but you'll need [the remote explorer (SSH)](https://code.visualstudio.com/docs/remote/ssh) at a minimum.

You'll also need to install the [Google Cloud SDK](https://cloud.google.com/sdk) (a command line tool for interacting with GCP; SDK stands for 'software development kit') on your computer. Once you have downloaded and installed it, run `gcloud init` to set it up. This is the point at which your computer becomes trusted to do things to your GCP account.

Anything the Google Cloud SDK can do, Python (and C, C++, C#, Go, Java, Node.js, PHP, and Ruby) can do too, if you'd rather work with them. (R isn't supported by the SDK yet.) However, here we'll follow the instructions for doing this all in the command line.

## Creating a Cloud VM Instance

You'll need a Google Cloud Platform (GCP) account. New accounts get some free credit but you'll typically need to add some billing information. Set up a new project on the Google Cloud Console, and enable the 'Google Cloud Compute API' (found under VM Instances).

Now you will set up a virtual machine. You can do this either through the set of menus or via the command line. For the menu options, go to the VM instances page and click 'Create Instance', then fill in the form with info on the computer you want.

If you're going for the command line approach, you can do this all in one fell swoop by running

```bash
gcloud compute instances create instance-name --project=PROJECT-NAME --zone=europe-west2-c --machine-type=e2-standard-2 --network-interface=network-tier=PREMIUM,subnet=default --maintenance-policy=MIGRATE --provisioning-model=STANDARD --service-account=PROJECT-NUMBER-compute@developer.gserviceaccount.com --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append --create-disk=auto-delete=yes,boot=yes,device-name=instance-1,image=projects/debian-cloud/global/images/debian-11-bullseye-v20220920,mode=rw,size=10,type=projects/chipshop/zones/us-central1-a/diskTypes/pd-balanced --no-shielded-secure-boot --shielded-vtpm --shielded-integrity-monitoring --reservation-affinity=any
```

where `instance-name` is the name you give the instance (you need to choose this now), `PROJECT-NAME` is the name of the project you've created, and `PROJECT-NUMBER` is the project number of that project. Note that these are fairly default settings with a London-based e2 machine running Bullseye Debian (a type of Linux).

If you did the above and all has worked you should now be able to see a new line in the VM instances page on the GCP pages that has a 'running' symbol under 'Status'; yes, your VM is already running! (And racking up costs but this is a small machine so not much cost per hour--but you may wish to turn on billing alerts at this point!)

You can jump straight to your new VM's command line using Google's simple approach by clicking on their 'SSH' button on the line where your running VM instance appears on the VM instances page. But this only gets a command line, not Visual Studio Code...

## Connecting to a running GCP Virtual Machine Instance from Visual Studio Code

Okay, so your GCP VM instance is running and now you're going to connect to it with Visual Studio Code.

First, we need to set up the SSH connection between your computer and your running cloud VM; essentially a way for them to talk to each other. You can find out more about SSH authentication [here](https://www.ssh.com/academy/ssh/protocol). Open up VS Code and its integrated terminal (<kbd>ctrl</kbd>+<kbd>`</kbd> shortcut on a Mac). Make sure you are in the correct GCP project by running

```bash
gcloud config set project PROJECT-NAME
```

on the command line. If you already tried this process and aborted it, you may need to remove your existing Google keys; they're stored in the directory `~/.ssh/`. Now create the SSH settings for your new instance using

```bash
gcloud compute config-ssh
```

You'll get a message like

```text
WARNING: The private SSH key file for gcloud does not exist.
WARNING: The public SSH key file for gcloud does not exist.
WARNING: You do not have an SSH key for gcloud.
WARNING: SSH keygen will be executed to generate a key.
Generating public/private rsa key pair.
Enter passphrase (empty for no passphrase): [can enter one here]
Enter same passphrase again: [can enter one here]
Your identification has been saved in /Users/USERNAME/.ssh/google_compute_engine
Your public key has been saved in /Users/USERNAME/.ssh/google_compute_engine.pub
The key fingerprint is:
SHA256:YOUR-FINGERPRINT USERNAME@LOCAL-COMPUTER-NAME
The key's randomart image is:
+---[RSA 3072]----+
|                 |
| TEXT-ART-IMAGE  |
|                 |
+----[SHA256]-----+
Updating project ssh metadata...⠼Updated [https://www.googleapis.com/compute/v1/projects/PROJECT-NAME].  
Updating project ssh metadata...done.
You should now be able to use ssh/scp with your instances.
For example, try running:

  $ ssh INSTANCE-NAME.europe-west2-c.PROJECT-NAME
```

Okay, this means your connection configurations have been set up successfuly. (Note: don't run `ssh INSTANCE-NAME.europe-west2-c.PROJECT-NAME` directly on your command line, as you will just ssh into the cloud instance's command line rather than open Visual Studio Code in the VM.)

Within Visual Studio Code on your local computer, go to the remote explorer tab, which you can find on the left hand side (you'll need to have installed the remote explorer package for SSH). Choose 'SSH Targets' from the drop-down menu at the top. Then you should see an entry listed for INSTANCE-NAME.europe-west2-c.PROJECT-NAME. Right-click on it and choose 'connect to host in new window'.

A new Visual Studio Code window will open and you will be asked whether you recognise the VM. Then you will be asked for a passphrase, if you chose to create one earlier.

Congratulations, you should now be on your VM instance using Code! You can check because the green text in the bottom left-hand corner of Visual Studio Code should read

> SSH: INSTANCE-NAME.europe-west2-c.PROJECT-NAME

First, you'll want to open up a folder to work in. Perhaps you want to git clone a repository and then open that? Git doesn't come pre-installed so you'll need to run `sudo apt-get install git` first. You can just open the home directory too. Either way, open up a folder.

## Using Python on your Cloud VM Instance

If you used Google's image "debian-11-bullseye-v20220920" then it will come with a version of Python already installed (Python 3.9.12) and you can check the version with `python -V` on the command line. Note that **pip** (used for installing Python packages) may not itself be installed--you can install it on Debian linux by running `sudo apt-get install pip` on the command line.

Next, you will need to install the Visual Studio Code [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) (65 million installs and counting) on *the cloud instance*. Do that, then open up a Python script (you can run `echo "print('hello world')" > hello.py` if you need inspiration for a simple script).

The interactive window depends on one package, `ipykernel`, that you probably don't have already. Once you've installed **pip**, you'll need to run `pip install ipykernel` on the command line.

Now, select the code you'd like to run in your Python script, right-click, and select 'Run Selection/Line in Interactive Window'. You can also hit <kbd>shift</kbd> + <kbd>enter</kbd> with the code selected.

You should find that a Visual Studio Code interactive window launches and runs your code on the cloud!

And notebooks work too--try `touch notebook.ipynb` on the command line, opening the file in Visual Studio Code, and then add `print("hello world")` to the first cell and run it.

### Setting up conda

Lots of data scientists use the Anaconda distribution of Python. It's not on the base image we're using, "debian-11-bullseye-v20220920", by default, though of course you could choose an image that does have it if you want, or roll your own, when you create your VM instance. If you're using this Debian option though, and you want to install Anaconda after the fact, the instructions are below. (We'll work with the light-weight Anaconda version called 'miniconda'.)

First you'll need the `wget` Linux programme. Run

```bash
sudo apt-get install wget
```

to grab that. Next, let's get the install script for Miniconda and run it:

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

bash Miniconda3-latest-Linux-x86_64.sh
```

This will install Miniconda. Relaunch the terminal and you should see the familiar `(base)` prompt appearing so that your VM command line prompt now looks like

```bash
(base) USERNAME@INSTANCE-NAME:~$
```

Another way to check is to run `conda info`, which will tell you all about your conda installation.

Now, due to the license on Anaconda, you may wish to set `conda install` to only grab packages from the `conda-forge` channel. You can do that with a couple of commands:

```bash
conda config --add channels conda-forge
```

to add conda forge as a channel for package downloads and put it first, and

```bash
conda config --set channel_priority strict
```

to get strict channel priority of conda forge, ie to always prefer that channel no matter what package is being installed. (It's a bad idea to mix the conda forge and default channels.)

## Moving Data In and Out of Your VM

Data scientists can't data science without data.

### Putting Data on the Cloud

There are many types of cloud data storage; here, we'll just use the most popular (but perhaps not the best for your particular use case so worth reading up on what would best serve your requirements).

To create a new cloud data bucket, which persists separately to any VM instances, the command is

```bash
gcloud storage buckets create gs://BUCKET_NAME --project=PROJECT_ID --location=BUCKET_LOCATION
```

For this project, we'll accept the defaults except for setting the location to "europe-west2". To upload data, it's

```bash
gcloud storage cp OBJECT_LOCATION gs://DESTINATION_BUCKET_NAME/
```

For example, to move a csv file called "glue.csv" that is in the working directory of the terminal,

```bash
glcoud storage cp glue.csv gs://DESTINATION_BUCKET_NAME/
```

After running this, you should be able to see the data appear in your bucket. The link to view it in the Google Cloud Console will be

```text
https://console.cloud.google.com/storage/browser?project=PROJECT-NAME&prefix=
```

and then click on the name you gave your bucket.

### Moving Data from a Bucket to Your VM (and back)

Okay, so now your data is on the cloud--but it's not on your VM! We're back in Visual Studio Code on the VM, and using the integrated terminal. To copy data from the bucket to the VM, the command to use *on the terminal in the VM* is

```bash
gcloud storage cp -r gs://BUCKET-NAME/ DESTINATION-FOLDER/
```

The `-r` flag makes this recursive, while `cp` means copy. So, following our example you could make a directory data `mkdir data` and then run

```bash
gcloud storage cp -r gs://BUCKET-NAME/ data/
```

To move any data back to the bucket when you are done is the same command you used for moving data onto the bucket in the first place, ie

```bash
glcoud storage cp FILE-NAME gs://DESTINATION_BUCKET_NAME/
```

## Finishing

Remember: best practice is to treat a cloud instance as temporary. Shunt data you want to save in and out when you use it, and use version control for code. And most of all, **don't forget to turn your VM instance off when you've finished using it!**

Hopefully this has been a useful summary of how to use Visual Studio Code in the cloud, especially using the interactive window for Python coding. Happy coding!
