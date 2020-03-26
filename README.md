# To run the WIP app:
1. You may need to create the folder "opt/python/log" (outside of the repo)
2. Run "python2 application.py"
3. The page will be up on http://localhost:8000

# To deploy on AWS:
1. Add any new dependencies to "requirements.txt"
2. Make a ZIP containing only the files (i.e., no parent folder)
3. Upload to AWS

# TODOS:
1. Refactor the HTML into a templates folder (with a styles folder for CSS) - DONE
2. Add framework for HTML (static) - DONE
3. Build out the backend (figure out how it can modified safely)

# Backend:
1. Google form (for input): should take in address, ZIP code, website, other info
2. Google sheet (linked to form, sends email notifications upon submission) - column for Verified?
3. Querying our site => querying the google sheet via AppScript (query on business type, location)
4. Add ZIP code api for location preferences?
