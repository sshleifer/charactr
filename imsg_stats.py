from subprocess import call
from chat_to_csv import main
import webbrowser as wb

main(hidegroups=True)
print "Serving scatterplot at localhost:8000"
wb.open("http://localhost:8001")
call("python -m SimpleHTTPServer 8001",shell=True)
#call("open -a safari index.html", shell=True)

