# Testing
![Test Pass](https://img.shields.io/badge/tests-passing-brightgreen)


| **Type of Testing**               | **Tool/Framework** | **Description**                                                   |
|-----------------------------------|--------------------|-------------------------------------------------------------------|
| **Backend Testing (Python)**      | pytest             | Testing Python code (e.g., Controllers, Models).       |
| **Frontend Testing (JavaScript)** | Jest               | Testing JavaScript code.  |
| **Web Browser Testing**           | Selenium           | Automating web browsers to perform end-to-end tests. |

## Backend Testing (Python-Flask)

To successfully reproduce the test results, ensure the following steps are followed:

1. **Disable or comment the `decrypt_file()` function in `app.py`.**
2. **In `main_controller.py`, disable or comment the `session.clear()` and `complete_stop()` functions.**
3. **In `video_controller.py`, disable or comment the `generate_frames()`.**



### **Pre-requisites for the Environment**

Ensure the following libraries are available in your environment for testing:


```sh
pip install pytest requests Flask pytest-cov coverage
```

### **To test Complete Code:**

```sh
pytest 
```
#### (Optional) For verbose and shows print() outputs during test execution 
```sh
pytest -vs    
```

![Image13](results/results_complete.png)

### **To test Indiviual Modules:**

```sh
pytest tests/test_app.py     
```

```sh
 pytest tests/test_controllers/test_main_controller.py
```

```sh
pytest tests/test_controllers/test_video_controller.py
```

```sh
pytest tests/test_models/test_decryption.py
```

```sh
pytest tests/test_models/test_forms.py  
```

```sh
pytest tests/test_models/test_sheets.py
```

```sh
pytest tests/test_models/test_state.py
```

```sh
pytest tests/test_models/test_tracking.py  
```

```sh
pytest tests/test_models/test_youtube_stream.py
```

---

## Frontend Testing (Javascript)
### **Pre-requisites for the Environment**
### 1. **Set Up Jest for Your Project**

Since your app is primarily a Flask app but includes JavaScript testing:
1. Navigate to `tests/test_javascript` directory:
    ```bash
    cd my_flask_app/tests/test_javascript
    ```

2. Dependencies are already present in package.json, so install directly:
    ```bash
    npm i
    ```
3. (Optional) To update all the dependencies and devDependencies to their latest versions:
    ```bash
    npx npm-check-updates -u
    npm install
    ```

---

### 2. **Run Tests**

Run Jest from the `test_javascript` directory:
```bash
npm test
```

If Jest still complains about module imports, ensure you run the test with the experimental modules flag:
```bash
node --experimental-vm-modules ../../node_modules/.bin/jest
```

![Image13](results/result_javascript.png)

