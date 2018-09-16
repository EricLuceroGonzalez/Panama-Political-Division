# Panama-Political-Division

Panama political division as a JSON file.

One key: Provinces --> value: and array of Objects. One for each province.
Each province: has:
      "id"
      "name"
      "superficie" (surface)
      "pop10"      (population)
      "den10"      (population density)
      "capital"
      "distritos"  (and Array of districts. Each districts has: same previous parameters plus:
                    a sub-division (corregimientos) multiple for each district.
