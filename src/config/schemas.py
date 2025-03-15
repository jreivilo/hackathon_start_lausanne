def get_analysis_schema():
	"""
	Retourne le schéma JSON pour l'analyse structurée.
	"""
	return {
		"properties": {
			"produit": {
				"type": "object",
				"description": "Informations détaillées sur le produit alimentaire",
				"properties": {
					"nom": {
						"type": "string",
						"description": "Nom du produit alimentaire"
					},
					"origine": {
						"type": "string",
						"description": "Origine du produit alimentaire"
					},
					"ingrédients": {
						"type": "array",
						"description": "Liste des ingrédients du produit alimentaire",
						"items": {
							"type": "string"
						}
					},
					"valeur_nutritive": {
						"type": "object",
						"description": "Valeurs nutritives de base du produit alimentaire",
						"properties": {
							"calories": {
								"type": "number",
								"description": "Calories dans le produit alimentaire"
							},
							"protéines": {
								"type": "number",
								"description": "Teneur en protéines en grammes"
							},
							"graisses": {
								"type": "number",
								"description": "Teneur en graisses en grammes"
							},
							"glucides": {
								"type": "number",
								"description": "Teneur en glucides en grammes"
							},
							"sucre": {
								"type": "number",
								"description": "Teneur en sucre en grammes"
							},
							"fibres": {
								"type": "number",
								"description": "Teneur en fibres en grammes"
							},
							"sodium": {
								"type": "number",
								"description": "Teneur en sodium en milligrammes"
							}
						}
					}
				}
			}
		}
	}
