
[![CESI](https://img.shields.io/badge/CESI-FISA_A4-yellow.svg)](https://www.cesi.fr/)


# FISA_A4-Systemes_automatises

 Ce projet fournit un script Python permettant de contrôler une imprimante 3D à distance en utilisant OctoPrint sur un Raspberry Pi. L'objectif est d'automatiser certaines tâches courantes via l'API d'OctoPrint.


![Logo](https://i.postimg.cc/1Rkvzjjp/image.png)


## Authors

- [@BennatFr](https://github.com/BennatFr) : Nathan FERRER
- Samuel BRUN
- Nicolas COULON
- Corentin HARDY
- Anne-Sophie BEAL
## API Reference

#### Checks if the printer is connected

```http
  GET /printer
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `api_key` | `string` | **Required**. Your API key |

#### Checks printer status

```http
  GET /api/printer
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `api_key` | `string` | **Required**. Your API key |

#### Send G-Code command

```http
  GET /api/printer/command
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `api_key` | `string` | **Required**. Your API key |
| `json` | `json` | G-Code command |

#### Capture an image from the camera connected to OctoPrint

```http
  GET /webcam/?action=snapshot
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `api_key` | `string` | **Required**. Your API key |
