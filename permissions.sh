for i in 1 2 3 4 5 6 7 8 9; do
   echo "Fixing agent $i ..."

   # make sure agents have their own group only
   sudo usermod -G "" "agent$i"
   sudo usermod -g "agent$i" "agent$i"

   # for logs and temporary files
   sudo mkdir -p "/home/agent$i/fast_data/logs"

   # agent should be able to modify all code
   sudo chown agent$i:agent$i -R "/home/agent$i/fast_data"

   # prevent "swap directories" attach
   sudo chown    jk:jk "/home/agent$i/fast_data"
   sudo chown    jk:jk "/home/agent$i"
   sudo chmod    a+r   "/home/agent$i"
   sudo chmod    o-w   "/home/agent$i"
   sudo chmod    o-w   "/home/agent$i/fast_data"

   # lock test cases
   sudo chown    jk:jk "/home/agent$i/fast_data/permissions.sh"
   sudo chown    jk:jk "/home/agent$i/fast_data/sync.sh"
   sudo chown    jk:jk "/home/agent$i/fast_data/run.py"
   sudo chown -R jk:jk "/home/agent$i/fast_data/missions"

   # no other backdoor
   sudo chmod -R o-w   "/home/agent$i/fast_data"
   sudo setfacl -b -R /home/agent$i

   # however `jk` has full access now and forever
   sudo setfacl -R -m u:jk:rwX "/home/agent$i"
   sudo setfacl -R -d -m u:jk:rwX "/home/agent$i"
done
