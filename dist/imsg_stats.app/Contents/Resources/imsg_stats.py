from subprocess import call
from chat_to_csv import main
main(hidegroups=True)
call("open -a safari index.html", shell=True)

