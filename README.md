# Phishing Domain Detector

This project checks whether a domain name is fake or genuine. You give it something like `paypal-login-secure.xyz` or a full link, and it answers Fake or Genuine along with how sure it is. It started as a copy of my student pass/fail project and uses the same setup: scikit-learn for the model, MLflow to keep track of training runs, FastAPI to serve it, and Docker with Render to put it online.

## The data

Training uses `dataset/phishing_domains_1000.csv`, which has 1000 domains, half fake and half genuine. Each row already comes with a set of measurements such as the length of the domain, how many dots, hyphens and digits it has, whether the ending (.tk, .xyz and so on) is one that scammers like, whether a well known brand name or a word like "login" or "verify" shows up in it, and how random the letters look. The model learns from twelve of these columns. The `technique` column is left out on purpose, because it describes how each sample was made (typo, real subdomain and so on) and would hand the model the answer.

The file `src/features.py` works out the same twelve measurements for any new domain you send to the API. I compared its output with the CSV and it matches on all 1000 rows. One thing to keep in mind is that 1000 fairly tidy examples is a small dataset, so the accuracy of around 98 to 99 percent will probably be lower on messy real-world domains.

## Training

Running `python -m src.ML_TRACKING` trains three random forests with different numbers of trees and different train and test splits, and writes each run to MLflow with its accuracy, precision, recall and F1 score. The best one by F1 is saved as `models/model.pkl`, and that is the file the API loads. Every time you train again the runs carry on numbering from where the last ones stopped.

To look at the results, start the dashboard with `python -m mlflow ui --backend-store-uri sqlite:///mlflow.db` and open http://127.0.0.1:5000. Everything is under the experiment called phishing, and you can tick a few runs and press Compare to see them side by side.

## The API

Start it with `python -m uvicorn src.app:app --reload` and open http://127.0.0.1:8000/docs to try it in the browser. Send a POST to `/predict` with a body like `{"url": "paypal-login-secure.xyz"}` and you get back something like `{"url": "paypal-login-secure.xyz", "result": "Fake", "fake_probability": 1.0}`. The `/train` endpoint retrains the models from the same data. `tests/test_api.py` sends a few sample domains if you want a quick check while the server is running.

## Running it yourself

Install the packages with `pip install -r requirements.txt`, train the model, and start the API as described above. Run all commands from the project folder.

## Docker and deployment

To build the image and run it locally use `docker build -t phishing-detection-api .` followed by `docker run -d -p 10000:10000 phishing-detection-api`, then open http://localhost:10000/docs. For hosting, the project runs on Render as a Docker web service with `/openapi.json` as the health check. The settings are in `deployment.yaml`. Render redeploys by itself every time I push to the main branch, and the GitHub Action in `.github/workflows/deploy.yml` only checks that the Docker image still builds, so there is just one deploy per push. The Docker image copies in `models/model.pkl`, so that file has to be committed to the repository or the build will fail.
