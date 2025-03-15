def get_analysis_schema():
	"""
	Returns the JSON schema for structured analysis.
	"""
	return {
		"properties": {
			"product": {
				"type": "object",
				"description": "Detailed information about the food product",
				"properties": {
					"name": {
						"type": "string",
						"description": "Name of the food product"
					},
					"origin": {
						"type": "string",
						"description": "Origin of the food product"
					},
					"ingredients": {
						"type": "array",
						"description": "List of ingredients in the food product",
						"items": {
							"type": "string"
						}
					},
					"nutritive_value": {
						"type": "object",
						"description": "Basic nutritive values of the food product",
						"properties": {
							"calories": {
								"type": "number",
								"description": "Calories in the food product"
							},
							"protein": {
								"type": "number",
								"description": "Protein content in grams"
							},
							"fat": {
								"type": "number",
								"description": "Fat content in grams"
							},
							"carbohydrates": {
								"type": "number",
								"description": "Carbohydrates content in grams"
							},
							"sugar": {
								"type": "number",
								"description": "Sugar content in grams"
							},
							"fiber": {
								"type": "number",
								"description": "Fiber content in grams"
							},
							"sodium": {
								"type": "number",
								"description": "Sodium content in milligrams"
							}
						}
					}
				}
			}
		}
	}
