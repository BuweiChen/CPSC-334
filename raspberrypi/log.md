Thursday 09/12/24 Lab 2

Goal: On raspberry startup, run a script that uploads the ip address to github

Recall from last lab: we made a script in Documents/raspberrypi that logs the ip address to github.

Here’s the complete code:
```
cd "$(dirname "$0")";
echo "Your public ip is: $(hostname -I)";
hostname -I > ip.md;
git add ip.md;
git commit -m "update ip!";
git push origin main;
```

1. Learn how to use systemd to run scripts on startup https://askubuntu.com/questions/919054/how-do-i-run-a-single-command-at-startup-using-systemd 
According to askubuntu:
```
[Unit] 
Description=Spark service 
[Service] 
ExecStart=/path/to/spark/sbin/start-all.sh 
[Install] 
WantedBy=multi-user.target
```
Replace with our own script/path/description of course

To enable it:
Place it in /etc/systemd/system folder with a name like myfirst.service.
Make sure that your script is executable with:
`chmod u+x /path/to/spark/sbin/start-all.sh`
Start it:
`sudo systemctl start myfirst`
Enable it to run at boot:
`sudo systemctl enable myfirst`
Stop it:
`sudo systemctl stop myfirst`

