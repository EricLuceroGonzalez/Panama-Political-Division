🇵🇦 Panama Political Division (JSON)
A comprehensive and fully structured JSON dataset containing the hierarchical political and administrative division of the Republic of Panama.

This repository is ideal for developers, data analysts, and researchers who need to implement geographic structures in their applications, such as cascading dropdown menus (Province ➔ District ➔ Corregimiento), geographic databases, or data visualization projects.

## 🚀 Features

Complete Hierarchy: Includes all Provinces, Comarcas, Districts, and Corregimientos.

Updated Data: Reflects the latest geopolitical changes and official subdivisions (including the 2023 Census data).

Unique Identifiers (IDs): Uses a relational ID system (e.g., `01` for Province, `01-01` for District, `01-01-01` for Corregimiento) for easy database integration.

Demographic Data: Includes surface area, population, and population density metrics.

## 🗂️ JSON Data Structure

The main JSON object contains a single root key called `"provincia"`, which holds an array of Objects representing each province or comarca.

### Data Schema
Each level of the hierarchy shares a similar set of properties:

Property	Type	Description
`id`	`String`	Unique hierarchical identifier.
`name`	`String`	Official uppercase name of the location.
`superficie23`	`String`	Surface area in square kilometers (km²).
`pop23`	`String`	Total population (based on 2023 Census data).
`den23`	`String`	Population density (inhabitants per km²).
### Hierarchy Breakdown

Provinces (Level 1): Contains the core stats and an array of `"distritos"`.

Districts (Level 2): Contains district-level stats and an array of `"corregimientos"`.

Corregimientos (Level 3): Contains the final subdivision stats.

## 💻 Code Example

Here is a snippet showing the nested structure of the data:

```json
{
"provincia": [
{
"id": "01",
"name": "BOCAS DEL TORO",
"superficie23": "4654.0",
"pop23": "159228",
"den23": "34.2",
"distritos": [
{
"id": "01-01",
"name": "BOCAS DEL TORO",
"superficie23": "285.0",
"pop23": "17274",
"den23": "60.6",
"corregimientos": [
{
"id": "01-01-01",
"name": "BOCAS DEL TORO",
"superficie23": "34.1",
"pop23": "6708",
"den23": "196.8"
}
]
}
]
}
]
}
```

## 🛠️ Usage

You can directly fetch the raw JSON file into your frontend or backend applications using the raw GitHub URL:

```javascript
// Fetching the data in JavaScript
const dataUrl = 'https://raw.githubusercontent.com/YOUR_USERNAME/Panama-Political-Division/master/panama_oficial_2023.json';

fetch(dataUrl)
.then(response => response.json())
.then(data => {
console.log(data.provincia);
// Build your dropdowns or seed your database here
})
.catch(error => console.error('Error loading Panama data:', error));
```

## 🗺️ Roadmap & Known Issues

This project is actively maintained, but there is always room for improvement. Below are some planned features and areas where community contributions are highly encouraged:

### 1. Geospatial Data (Polygons & Coordinates)
Currently, this repository only provides tabular and hierarchical data.

Goal: Expand the dataset to include GeoJSON or TopoJSON structures with `MultiPolygon` coordinates for every Corregimiento, District, and Province. This will allow developers to easily render interactive maps of Panama (e.g., using Leaflet or Mapbox).

### 2. Data Verification & Edge Cases

Issue: Panamanian political division changes frequently due to new legislation (e.g., the creation of the Naso Tjër Di Comarca or the Tierras Altas District).

Goal: Establish a regular verification routine against the Electoral Tribunal (TE) and the National Institute of Statistics and Census (INEC) to ensure 100% accuracy of names, IDs, and borders.
You can check the official website of the [National Institute of Statistics and Census (INEC)](https://www.inec.gob.pa/publicaciones/Default3.aspx?ID_PUBLICACION=1199&ID_CATEGORIA=19&ID_SUBCATEGORIA=71)

### 3. Historical Tracking

Goal: Include a `historical_changes` array or property to track when a corregimiento was segregated, merged, or renamed. This is crucial for applications dealing with historical data pre-2023.

### 4. Lightweight Version (Minified)

Goal: Provide a `panama_min.json` containing only IDs and Names (excluding population and surface area) for lightweight frontend applications where payload size is critical.

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

Don't forget to give the project a star! Thanks again!

Fork the Project

Create your Feature Branch: `git checkout -b feature/AmazingFeature`

Commit your Changes: `git commit -m 'Add some AmazingFeature'`

Push to the Branch: `git push origin feature/AmazingFeature`

Open a Pull Request

## 📄 License
This project is open-source and available under the MIT License.