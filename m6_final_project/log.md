12/12 2:11 PM

So far I've just been printing parts from https://www.littlefrenchkev.com/bluetooth-nerf-turret

After 3 failed attempts I switched to tree supports. These look way better than before and I just need to print the legs now

Just got the motor to work with the MOSFET, so now I have an electronic switch to control the motors

Moving some code and reference code into the template so I can keep track.

next up is just verifying and assembling the 3D print

12/12 10:41 PM

Just spent the better part of 4-ish hours making a housing for the laser. Might have been grief for me but I think it's worth it. Guess we'll see. Just started print and I will check back in 3.5 hours. Time to write some code for the esp32 sense

12/13 12:10 AM

Finally got the seeed sense to work. Video seems chopy. I suspect it's because it's over heating. Need to try to power it with less wattage.

12/13 12:33 AM

Think I got it to work better, followed this comment on reddit https://www.reddit.com/r/esp32/comments/c4iy1j/comment/m1d3a92/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button

Will also try antanna shielding

12/13 4:07 PM

Prints turned out super well, so I'm just assembling now. Went to pick up the nerf darts and servos. Got cooked by the fun police (no 200 mW laser in doors sadge). Might need to pick up some metric counter sunk screws later since the ceid apparently doesn't have those. The ceid staff is also leaving and locking the stuff up as we speak, so hopefully I have all I need for the time being.

12/13 5:05 PM

Finished assembling it. IT LOOKS SO SICK. Gotta reprint 2 parts I think. One is the right laser housing, the front is interfering with the fly wheel. Second is the neck (idk what to call it), just need to invert it since I inverted the direction where I'm attaching the top and neck--to give it more range of motion. But overall AMAZING success!

PS: just started print of the replacement parts. Chose some cool colors. Checking back in in an hour.

PS 2: probably need to reprint the esp32/buck mount too. esp32 measures 27.1 mm across and the buck is 20.3 mm

12/13 8:32 PM

Print came out great. Just assembled most of it. All there's left of the build is just getting the laser trigger part assembled, which I just started a print for. Time to say goodbye to the janky popsicle stick!

12/14 3:16 AM

To say I've been through hell and back in the last 6 hours is the understatement of the century. I don't have much battery left so I'll make it quick. I have learned so much about building with hardware and designing with computers during this project it's not even funny.

I finished the electronics. The diode was giving me so much trouble because it's near impossible to coax it to go through the motor leads like I want it to. I messed it up at least 5 times (spin direction was wrong, diode orientation wrong, pulled off motor lead, to name a few).

Somehow the mosfet stopped working, and I had to pull off the resistor to make it work. Only god knows why.

The highlight of the electrical build was definitely figuring out how the MTA connectors worked. There's this gun shaped thing in the drawers that you need to use on the connectors and it only works with solid core wires with no lead. I had to redo so much just because I was using the connectors incorrectly and through troubleshooting in general.

I'm so glad I ended the night having saw my turret fire.

12/14 6:14 PM

Got bluetooth to work

12/14 7:30 PM

Nevermind--seems to be some problem with mac. Connection keeps dropping after a couple of seconds. Tried reconnecting, forgetting, deleting existing bluetooth connections, resetting mac bluetooth module (3 ways). To no avail. Switching to wifi it is then.

12/14 7:52 PM

Might be a brown out issue? Wifi kept shutting off too so I'm guessing either the 9v or the 3 amps is too much.