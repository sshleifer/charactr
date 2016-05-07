from subprocess import call
import webbrowser as wb

print "Serving scatterplot at localhost:8000"
wb.open("http://localhost:8014")
call("python -m SimpleHTTPServer 8014", shell=True)
