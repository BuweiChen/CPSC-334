#!/bin/bash
 
# wanIp="$(curl https://ipinfo.io/ip 2>/dev/null)";

# echo "Your public ip is: ${wanIp}";
echo "Your public ip is: $(hostname -I)";
hostname -I >> ip.md;
git add .;
git commit -m "update ip!";
git push origin main;