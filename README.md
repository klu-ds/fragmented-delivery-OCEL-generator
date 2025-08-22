# FrOG: fragmented-order-generator

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the dependencies from the requirements.txt file.

```bash
pip install -r requirements.txt
```

## Start

Start FrOG using the app.py file

```bash
python app.py
```

This will start dash:

```bash
Dash is running on http://127.0.0.1:8050/

 * Serving Flask app 'app'
 * Debug mode: on
```

Go to the address where your app is running to access FrOG.

## Usage

1. On the simulation page, configure your global simulation parameters.
2. Configure as many items for your warehouse as you like (at least 1).
3. Run the simulation, once its done the results will appear on the simulation page.
4. To access the created OCELs, go to the analysis page. There you can see basic information and download the OCEL

5. To benchmark the tool use the benchmark page, where you can configure simulation days, amount of items and splits.

## License

[MIT](https://choosealicense.com/licenses/mit/)
