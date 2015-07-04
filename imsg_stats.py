from subprocess import call
from chat_to_csv import main
import webbrowser as wb

main(hidegroups=True)
print "Serving scatterplot at localhost:8000"
wb.open("http://localhost:8002")
call("python -m SimpleHTTPServer 8002",shell=True)
