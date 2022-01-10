import { AxModel, AxSelectorObjects } from "./model";
import { GroupsFlag } from "../ax-designer/ax-global";

import { SelectorMock } from "./mockSelector";

export class AxModelMock {

    static resolution = '1440*900@100';

    static getSelector():AxSelectorObjects {
        return SelectorMock.selectorMock;
    }

    static get():AxModel {
        return this._model;
    }

    static flags():GroupsFlag {
        return this._flags;
    }

    static _flags:GroupsFlag = {
        created: [true,true,true],
        count: [3,3,4],
        main: [true,true,true]
    }
    static _model = {
        "object_name": "test",
        "maps": {
          "test": {
              "bla1": "BLA1",
              "bla2": "bla2"
              },
          "test2": {
              "bla1": "BLA1",
              "bla2": "bla2"
              }
        },
        "detection": {
            "type": "appear+disappear",
            "timeout_s": 10,
            "break": true
        },
        "call": {
          "type": "run",
          "features": {
            "path": "test path",
            "arguments": "test arguments",
            "process": "test process"
          }
        },
        "box_list": [
            {
                "id": "sadfsafd",
                "x": 219,
                "y": 148,
                "w": 63,
                "h": 56,
                "roi_x": 205,
                "roi_y": 134,
                "roi_w": 91,
                "roi_h": 84,
                "roi_unlimited_left": false,
                "roi_unlimited_up": false,
                "roi_unlimited_right": false,
                "roi_unlimited_down": false,
                "group": 0,
                "is_main": true,
                "thumbnail": {
                    "group": 0,
                    "h": 24,
                    "image": "iVBORw0KGgoAAAANSUhEUgAAADAAAAAeCAIAAADlxgqWAAACz0lEQVRYCc3BfWjMcRwH8Pd7hrtT1M9DNLEhdpunaKxNQymMTUaE+SkPN2Mlwz9TiMIQR9L8aHLL44SQ3Zb8QXPKc+034ybEP8KldNrXzj6W/HGLu7la5/d6UUQQhiRi50xLM01Tqe+AoJ1A0IGIAHDYbSQRFSsqKvBLMBgsLS0lidg5nWmmaSqlBH8QEfzmsNtIIiqKCMKQROxSnU7TbFRKoQMRQTiH3UYSUdHr9eIXpVR+fj5JxC7V6TTNRqUU2okI/s5ht5FEVBQRhCGJ2I1KTTXNRqUUonLYbSQRFUUEYUgidumjR9fW1YZaQwJABIC0AyACQASACGC32QYnJSEqoqPuiYmtoRD+H8JiCIshmABpSyDaBPHSDfiBCIh4c+ma4QkgEsqT8gfj100atOrN3Q2hB9tW1JQcKuyV4ajuoX+8X1XiK1pYYn5BJzb6KjMyZ9oKHs+/kjfsfXWO89KSrxdmTdtc33Rgwbm1M/sVF7ckT667/bQs+wUH3NY1wxNAJOzdE+db/HvdzY0bZ+dclIYzVd1u6uXfX5XvezP2nvHh08PL9a/QCVdBohHc56/duW1rZih5/ZQxGcmZA+cBEBFyyLXdo/LLhhT2rky50bAr54iuGZ4AIqGItwbDcxPmSlvT4WxWp3i+XNL3t/hzE+ZKWxNqiphroBOuR/U7+jWvG7ri6vuXlYMzbrnTz1annJozZ1zZ0glP3Zvf/XietylJ14zh1xu2Zx/RNcMTQCREFyhZ3ffoyc/oEkTXICDoCsTfuXTN8AQQf8xbvPzbk6rWlIl3al+P0QJ9phePDPoqvZN0zfAEEH98drxgXNHle2+rsoYec2f5Do04+vB0UX+u1zXDE0D8EYDfneWfsT932Q13rz3zXYvqsg6uGblzYeKJleVTUXpiyyIfrummQnwQ/4SAIC4IiyEshrAYwmIIiyEshrAYwmIIi/kJH40cLmTkSrgAAAAASUVORK5CYII=",
                    "image_h": 30,
                    "image_w": 48,
                    "is_main": true,
                    "w": 27,
                    "x": 10,
                    "y": 3
                },
                "type": "I",
                "features": {
                    "I": {
                        "colors": true,
                        "likelihood": 0.9
                    },
                    "R": {},
                    "T": {}
                },
                "mouse": {
                    "type": null,
                    "features": {
                        "point": {
                            "dx": 0,
                            "dy": 0
                        }
                    }
                },
                "keyboard": {
                    "string": "",
                    "delays_ms": 100,
                    "durations_ms": 100
                }
            },
            {"id": "sadfsaf23d",
                "x": 140,
                "y": 220,
                "w": 62,
                "h": 45,
                "roi_x": 128,
                "roi_y": 208,
                "roi_w": 86,
                "roi_h": 69,
                "roi_unlimited_left": false,
                "roi_unlimited_up": false,
                "roi_unlimited_right": false,
                "roi_unlimited_down": false,
                "group": 0,
                "is_main": false,
                "thumbnail": {
                    "group": 0,
                    "h": 26,
                    "image": "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",
                    "image_h": 30,
                    "image_w": 48,
                    "is_main": false,
                    "w": 36,
                    "x": 5,
                    "y": 1
                },
                "type": "I",
                "features": {
                    "I": {
                        "colors": true,
                        "likelihood": 0.9
                    },
                    "R": {},
                    "T": {}
                },
                "mouse": {
                    "type": null,
                    "features": {
                        "point": {
                            "dx": 0,
                            "dy": 0
                        }
                    }
                },
                "keyboard": {
                    "string": "",
                    "delays_ms": 100,
                    "durations_ms": 100
                }
            },
            {
                "id": "sadfsaf4453d",
                "x": 380,
                "y": 274,
                "w": 77,
                "h": 30,
                "roi_x": 369,
                "roi_y": 263,
                "roi_w": 99,
                "roi_h": 52,
                "roi_unlimited_left": false,
                "roi_unlimited_up": false,
                "roi_unlimited_right": false,
                "roi_unlimited_down": false,
                "group": 0,
                "is_main": false,
                "thumbnail": {
                    "group": 0,
                    "h": 14,
                    "image": "iVBORw0KGgoAAAANSUhEUgAAADAAAAAeCAIAAADlxgqWAAADsElEQVRYCc3BfUyUBRwH8O/vjpedykvhiaBuik4y1MnAImQ3A0Rqu0pJbpeT19wQGxwR0CxSO19WGLIpbIcKeKW5LrBA53jblCFhKjglQrIDGU2UgRIo3Nvz64Xmphjds/XH8/kQRHo1MtJmtQHMAJgZAIPBYDAYDAaDwWCZTN76QwtEIkgMQWIIEkOQACKFUulJgnVozEEQgwjMmAYBjCdk13RXv7H0FoPxrxQeui3WolILNmQaCdP6pu26/8R4RHjKw+HD5ruzVyx73TxYbxYC22pNq1/bpFHKWlkwd/Y5Wg+5R+01xfvXhRQWxnrdykl88+aDnuu9/QWpQcdqlTV5qnOqE0lePj27lyWcxxQKj6xTmUNnfh247Z1KmCQDBDxtni7XZvz83vCsjeWrqpI7g9ZpHU3qvPjY5JsVCYNJxtCCUNPLFxpUMzc3tGREh391do+nIq38F1NT3/my9eX7VTO0TVczyjqiWxPDjLbacNfY+ErhZBxhCoVHVoL9oGEcb2Uep7bTKS1rDNlzNN/G1asrR/Gki3e6uGckIjzl4XDxT+aJl0LTbjTErYhur9PdjSlaUxJSGnXl50CK7u7NX7rwSGuJb/zVrV+nzP69fn/Azi8CKbq7d0di2cLq4PrQM2tPJHk/asyK2d0OxlNmeOV/6KP/xAzNjrOESQQw/hMRmEEEZjxGBGYQgRkEMP5BBGZMIoAxPQIYAEFiCCKQq6tMYJnDbndzdyPAYrEAcHF1s9us+J8QRJjbfGlbhXmlUas/ormd2L93+8W0YsW8e31f5gZHVvTjT6dsI5tdvRz4yytak9/3m6oeQRSCCHObL22rMK80aj+tN6j0A6EdO7fIV3+w+PLBnGPvqlMNwPIBvjZS+tHzi/ves+5LX+UT3FflGZYEMQgiKJvbdRVdLxq1esOGjvuFN95f9MKhXqG7OC/344wFXvMBHB0wb/cPsGiaC65FVAWVK2uTq0chCsFZipKOHx+kB4/tajwQmVujG11fNDT2ndoy2OmztcUz5jPNbw26HEXpkuPr6rLC4mae9NUfVefX5j3n9/YeiEEQhwCGDBDgJCIww3kEiSFIDEFiCBJDkBiCxBAkhiAxBIkhSAxBDBd/sAPPJIyAJzBJ7ovHhBHwBJxHcJrHOzL3KMGGZ2DAbRb8Ghb59y65HNYoDxDkMjn+5jKf+qPscBrBaX6n5Qne6buWH8AUBLpw/1zNlQUD44qxyuyQ7LX7unLnKOQAZN64s9EBp/0BFUR16J2Q0N4AAAAASUVORK5CYII=",
                    "image_h": 30,
                    "image_w": 48,
                    "is_main": false,
                    "w": 36,
                    "x": 5,
                    "y": 7
                },
                "type": "I",
                "features": {
                    "I": {
                        "colors": true,
                        "likelihood": 0.9
                    },
                    "R": {},
                    "T": {}
                },
                "mouse": {
                    "type": null,
                    "features": {
                        "point": {
                            "dx": 0,
                            "dy": 0
                        }
                    }
                },
                "keyboard": {
                    "string": "",
                    "delays_ms": 100,
                    "durations_ms": 100
                }
            },
            {
                "id": "sadfsafsdfasd",
                "x": 389,
                "y": 21,
                "w": 72,
                "h": 82,
                "roi_x": 374,
                "roi_y": 6,
                "roi_w": 102,
                "roi_h": 112,
                "roi_unlimited_left": false,
                "roi_unlimited_up": false,
                "roi_unlimited_right": false,
                "roi_unlimited_down": false,
                "group": 1,
                "is_main": true,
                "thumbnail": {
                    "group": 1,
                    "h": 19,
                    "image": "iVBORw0KGgoAAAANSUhEUgAAADAAAAAeCAIAAADlxgqWAAAFpUlEQVRYCc3BfVDTdRwH8Pfn99t4HGvjaeCotMID08SndDhJkwj1KJHTLKKULFNI7+Qq6MmSNAtNRGkoISpqKqXppWTZlZ4HRiblgRMQUxwTeWiMNtj47bdvOY+7uLb+yD/a60XwMgQvQxgqc8f5qjdm32hvx7/S6XQOUXSKTqdTFJ3O46Km7oM5JpMJnvFhaLvQ3mm7iUG67/FJ5ljZdgRK+ZuLRbhQXXUVx5GvRNpvs4VE3P30D6orbR3fpXQM2Aeqjn+Tl78J7pTt2KFUKOASFBjwXutYm4M158aazWZ4wIei90K/NJTHoGmftpOP/9klYart/M2XRLjQdUNre4eFwHx9OI7j3ztj6zT3FaWPDgvgWs4emZr8NNwpLf10yZIXMChj50Wb4Mx7LCpEGTRcIYE7fCi6fjb7hftg0FMldT4Bsg/TR1kMwtgYf7jQrxcuEoEIokPkeOJ5fuS9qoR9A/eJhiXqhhkpz8Odbdu2TdVqcRsDwHief6E6xGHurl0VC3f4EBh/7AxQ+WGo5Ep7R5ep+bVouNC1a1cADAwIxvZeMISHy9RRkfZ+W51BCDX/NH76PLij0+mmJSSAAQQwxgCeuNhRMUv3tWxPj4Y7fDCunmkraHpnjGa01WaR+QUxsEM/Hvgy8eT9a/SG9ZPgQo3NTczJADDiRMEhY+fI0dYrTZUH+Vyvr9bOToc7W4uLs5Yvx1AOUZRKJPCAD0bz91fXX3oz+8lV5j6TMjDYyVjxqY1rJxRN3x1Xv8oAF2poqB+wCwOCEBGhMunfEi7v8ZXCKowY9sRJo75W8/hCuFNUtCUqSo2hUlNTiQge8Eo0fNu04dLqZakrzH09ikAlL+U3n/xo3bgtM3dNbHjdABdqbGk2t9+U+kpDwiMvHhgfdc8YW2uNf6BdNqel16gfo5kDdzYVbs7OzgYYGBhuYYxxHCeV8PCAU+CXqvpNl97PXrCyx9rjTwHRV/tkE5MtXV0JJeP0bxvgQt9+Xgow4jiOqNd47H7hUFAkfmkbFhG3WXBiWuJ8uLPx400LFszHbYwxEAC1Ws1zBA84BWqPnN/atD7nudd7rKYACni1+NrB+GfEB9unF4/Xr2mDC0WEhwLgeRIcjrTijqNFex8dd/SEodD3XEKf1dz9uwnuFGzYOGXywxhKq9USETzg7sKZL86qoyPhQkT+/v4ArFbr4yXxjeuNcCH8zciU/TfOl4j9zcFJtYb9anim0cTbbP2Mgbk42W3Oiw0N8IBTYOEb82yiDf9QYzx9Y4sFLgQvQ/gbwi0MBDD8JwQw3BGqWBjz7GfHystasnNPbU2pzzzMKqY2vvx1Y0BUxtKIivyzppprYvzwUNwS1FVTEDJlqRXIOmTdlSYfl1G59t2YguRJJy5ZfXgC1MWVhRNkXVNmLcMgxtiJ66YFDwRfbtgTHp377LY965xvhUdG+c3dX91xWBM2l4gYY05R4CU+AAhQJ8wYlU6nWlsGSjtjoxZ/HFH34vHqpNyjH1akDVNN0BZkKGZmHQagHJb6UNg5u3L+7M0rl8vrNkyfW6U9WJJRaz79zfvGFWXlqUlxT8QuXpF2/e1lG+Pq2K4x5A/g9L5MpcIvb7buK1DMrGUT056fmKAaHu0zlyJ//uNozWuvrtQ1PpKYHO0QvrI/V33MQfAyBC9D8DIEL0PwMgQvQ/AyBC9D8DJUWFjIufA8L5fLfzOJI5R8T09PVlYW/g9UXl5ORAaDwWKxaDSaNU33GXuFXdO6kpKS4Fl5efmiRYswaMbOzpzICynJibhjtHfv3pycHLlc3t3dLZFIjhyoGD1CFbfTcXn1BHhWVlaWmZmJQdotTXZpUJp5d15uLu4MVVZW5ufnq1QqvV4PIDEx8YPVeTMPCPrVU5jdAg9KS0vj4+MZAIa/RCp8OWByhf0RWWvpK7NwB/4EzjNkqUivr2EAAAAASUVORK5CYII=",
                    "image_h": 30,
                    "image_w": 48,
                    "is_main": true,
                    "w": 17,
                    "x": 15,
                    "y": 5
                },
                "type": "I",
                "features": {
                    "I": {
                        "colors": true,
                        "likelihood": 0.9
                    },
                    "R": {},
                    "T": {}
                },
                "mouse": {
                    "type": null,
                    "features": {
                        "point": {
                            "dx": 0,
                            "dy": 0
                        }
                    }
                },
                "keyboard": {
                    "string": "",
                    "delays_ms": 100,
                    "durations_ms": 100
                }
            },
            {
                "id": "sadfsafd57fhfd",
                "x": 574,
                "y": 46,
                "w": 80,
                "h": 86,
                "roi_x": 558,
                "roi_y": 30,
                "roi_w": 112,
                "roi_h": 118,
                "roi_unlimited_left": false,
                "roi_unlimited_up": false,
                "roi_unlimited_right": false,
                "roi_unlimited_down": false,
                "group": 1,
                "is_main": false,
                "thumbnail": {
                    "group": 1,
                    "h": 19,
                    "image": "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",
                    "image_h": 30,
                    "image_w": 48,
                    "is_main": false,
                    "w": 18,
                    "x": 14,
                    "y": 5
                },
                "type": "I",
                "features": {
                    "I": {
                        "colors": true,
                        "likelihood": 0.9
                    },
                    "R": {},
                    "T": {}
                },
                "mouse": {
                    "type": null,
                    "features": {
                        "point": {
                            "dx": 0,
                            "dy": 0
                        }
                    }
                },
                "keyboard": {
                    "string": "",
                    "delays_ms": 100,
                    "durations_ms": 100
                }
            },
            {
                "id": "sadfsafd3453fsdfs",
                "x": 793,
                "y": 63,
                "w": 91,
                "h": 52,
                "roi_x": 780,
                "roi_y": 50,
                "roi_w": 117,
                "roi_h": 78,
                "roi_unlimited_left": false,
                "roi_unlimited_up": false,
                "roi_unlimited_right": false,
                "roi_unlimited_down": false,
                "group": 1,
                "is_main": false,
                "thumbnail": {
                    "group": 1,
                    "h": 20,
                    "image": "iVBORw0KGgoAAAANSUhEUgAAADAAAAAeCAIAAADlxgqWAAAC/UlEQVRYCc3BcWhUBRzA8e/vvXfutkRwMp27zWtzrrF0NYkc0rbYbo5A5vrDzAQneJQ1qCCphGEpwzYtKMuoKHGOIamRCiFzN0VpExRK1jSH01GzieSWOQe33t775W5FCwQv5OJ9PkKCmaZJHBzHIUbwGMFjpDBzevfV20wloALKFCKocv8KlhZd6PqeuykuWzb0wzHhb6YhjqtMqCqn7QQoU2VtyRpoGMAGDMFV7sIAlxgDXMAAl6na9GKV5IugyiTDENdVTL/lRJt7O2Vf3YLSj9oD6R+XXN9Z/4JVP+vA2W07yjjepFosMw/W3F7+9Xf+wM7Cwb3VgT98zZd3v/Ls8rn9uyI3+LdFoV3Dp+oO9DUXDtnTi8Id+vuK8s3uiRvhnNYPvtouRa8TE1E7JGmfl9xc8WFD2qP1c1NXvZz25aZe7kiZk7N50c+yr25B8K3tS2d/tjK5I7x22tvpe05vOVxCyw7VYpndmDW8rmt3+pKe+YP7Vwd+MpoHt4YyILc2o++RlY8lPx1+8ckNxOSXvTNwctNIf6uRvWZvpGtOxeNVYsEzNTP2H7rFseNHlpVXA+06VikL30i+VPlJbe3ll37ZuvbNnN7GK5ASqAleO/SjK8QYJq5jggOIGKqugDLh1NFXS5963zRNx3F8YDNJQAEBZYKA8g8DXCZZMA5UVFRY08bbjp4ERFDlL77cUGkweqv/27NXAOFeFj6c2XP+KvdHBFXiIXiM4DGCxwgeI3iM4DGCxwgeI3iM4DGCxwgeI3iM4DFCHGYVhoa6I/wvhHuZV/l89nMNFw++d/2bJhJPiEP+a4dnFpScXp9K4glx8AcKECOnMuxY/l/Pdw53tZAwQtyWvHvOl5rZ88XGm517SBghbsHVTUZqMDl78YWNeSSM+JOSbNt2VU3T9FlWdGxMRCzTssdtVbVM647oWJT/IiX9oflPrJqRknTttxEHrVqch2pR/rzG1ojAtg3VuQ9mHGk/09Jx7oHMPL30qYz2+qzRvm5ndMT9EzFwC3jr0K6dAAAAAElFTkSuQmCC",
                    "image_h": 30,
                    "image_w": 48,
                    "is_main": false,
                    "w": 36,
                    "x": 5,
                    "y": 4
                },
                "type": "I",
                "features": {
                    "I": {
                        "colors": true,
                        "likelihood": 0.9
                    },
                    "R": {},
                    "T": {}
                },
                "mouse": {
                    "type": null,
                    "features": {
                        "point": {
                            "dx": 0,
                            "dy": 0
                        }
                    }
                },
                "keyboard": {
                    "string": "",
                    "delays_ms": 100,
                    "durations_ms": 100
                }
            },
            {
                "id": "sadfsafd3242342",
                "x": 322,
                "y": 429,
                "w": 23,
                "h": 27,
                "roi_x": 312,
                "roi_y": 419,
                "roi_w": 43,
                "roi_h": 47,
                "roi_unlimited_left": false,
                "roi_unlimited_up": false,
                "roi_unlimited_right": false,
                "roi_unlimited_down": false,
                "group": 2,
                "is_main": true,
                "thumbnail": {
                    "group": 2,
                    "h": 19,
                    "image": "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",
                    "image_h": 30,
                    "image_w": 48,
                    "is_main": true,
                    "w": 16,
                    "x": 15,
                    "y": 5
                },
                "type": "I",
                "features": {
                    "I": {
                        "colors": true,
                        "likelihood": 0.9
                    },
                    "R": {},
                    "T": {}
                },
                "mouse": {
                    "features": {
                        "point": {
                            "dx": 0,
                            "dy": 0
                        },
                        "button": "left",
                        "amount": 1,
                        "delays_ms": 100,
                        "pixels": 100
                    },
                    "type": null
                },
                "keyboard": {
                    "delays_ms": 100,
                    "durations_ms": 100,
                    "string": "sss"
                }
            },
            {
                "id": "sadfsafd234sdfs",
                "x": 689,
                "y": 238,
                "w": 4,
                "h": 4,
                "roi_x": 681,
                "roi_y": 230,
                "roi_w": 20,
                "roi_h": 20,
                "roi_unlimited_left": false,
                "roi_unlimited_up": false,
                "roi_unlimited_right": false,
                "roi_unlimited_down": false,
                "group": 2,
                "is_main": false,
                "thumbnail": {
                    "group": 2,
                    "h": 4,
                    "image": "iVBORw0KGgoAAAANSUhEUgAAADAAAAAeCAIAAADlxgqWAAACWklEQVRYCb3B104UURzA4d85c8PtNiwwuzPDFnalPMbZR1AfQkEFBaSIBUssIGQXr409YkTKLoQSRqNEjSXqE/AOXJr8k0n2Ym4536ewpf2xgwjNP8B1XeIobGmfcxB75i/gui5xFLZkHjmIveofwHVd4ihsyTx0ELvmN5DNZomj2traDg8POXqZBw5ix/wCstkscdTIyMjMzAxHL3PfQWybn0AulyOO6ujoODg44Ohl7jmIreoPIJfLIbqeJGihsCVz10Fsmu+A53mI/GJy/PQ0EYUt6TsOYtN8AzzPQxQWU+NnpokobEnfdhAb5ivgeR6isJieODtNRGFL+paDaJh9wPd9RHExQwuFLembGrFu9gHf9xGlemb9fEhEYUv6hkasmS+A7/uI7nr7+kBIRGFL+rpGrJrPgO/7iHL92PpgSERhS+qaRqyYT0AQBIhy/TgtFLakpjTig/kIBEGAqNRONC6FRBS2pCY1YtmEQBAEiFO1k42hkIjCltS4Rryv7gFBECB6ah2N4ZCIwpbUVY14Z3aBrq4uRG+tkxYKW1JjGrFkdoB8Po/oXehsjIREFLYkRzViyWwD+Xwe0bvgNkdDIgpbklc04m11CygUCojeebc5FhJR2JK8rBFvzCZQLBYRffNZWihsSQ5rxGuzAZRKJUTfXLY5ERJR2JIc0ohXpgmUSiVE/1yuORkSUdiSvKgRL6sNoLu7G9E/m2tOhUQUtiQuaMQLswaUy2VE/6xHC4UtiUGNeG5WgUqlQhyFLYkBjXhmVoBKpUIchS2Jcxrx1CwDPT09xPkP1/mI786XR1MAAAAASUVORK5CYII=",
                    "image_h": 30,
                    "image_w": 48,
                    "is_main": false,
                    "w": 4,
                    "x": 22,
                    "y": 13
                },
                "type": "R",
                "features": {
                    "I": {
                        "colors": true,
                        "likelihood": 0.9
                    },
                    "R": {
                        "width": {
                            "min": -6,
                            "max": 154
                        },
                        "height": {
                            "min": -4,
                            "max": 12
                        }
                    },
                    "T": {}
                },
                "mouse": {
                    "type": null,
                    "features": {
                        "point": {
                            "dx": 0,
                            "dy": 0
                        },
                        "button": "left",
                        "amount": 1,
                        "delays_ms": 100,
                        "pixels": 100
                    }
                },
                "keyboard": {
                    "string": "ssss",
                    "delays_ms": 100,
                    "durations_ms": 100
                }
            },
            {
                "id": "sadfsafdasdfas1212",
                "x": 705,
                "y": 216,
                "w": 35,
                "h": 42,
                "roi_x": 694,
                "roi_y": 205,
                "roi_w": 57,
                "roi_h": 64,
                "roi_unlimited_left": false,
                "roi_unlimited_up": false,
                "roi_unlimited_right": false,
                "roi_unlimited_down": false,
                "group": 2,
                "is_main": false,
                "thumbnail": {
                    "group": 2,
                    "h": 19,
                    "image": "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",
                    "image_h": 30,
                    "image_w": 48,
                    "is_main": false,
                    "w": 16,
                    "x": 15,
                    "y": 5
                },
                "type": "T",
                "features": {
                    "I": {
                        "colors": true,
                        "likelihood": 0.9
                    },
                    "R": {},
                    "T": {
                        "type": "scraper"
                    }
                },
                "mouse": {
                    "type": "release",
                    "features": {
                        "point": {
                            "dx": 974,
                            "dy": 243
                        },
                        "button": "left",
                        "amount": 1,
                        "delays_ms": 100,
                        "pixels": 100,
                        "direction": "down"
                    }
                },
                "keyboard": {
                    "string": "sdgf",
                    "delays_ms": 100,
                    "durations_ms": 100
                }
            },
            {
                "id": "sadfsafdadsa212",
                "x": 705,
                "y": 216,
                "w": 35,
                "h": 42,
                "roi_x": 694,
                "roi_y": 205,
                "roi_w": 57,
                "roi_h": 64,
                "roi_unlimited_left": false,
                "roi_unlimited_up": false,
                "roi_unlimited_right": false,
                "roi_unlimited_down": false,
                "group": 2,
                "is_main": false,
                "thumbnail": {
                    "group": 2,
                    "h": 19,
                    "image": "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",
                    "image_h": 30,
                    "image_w": 48,
                    "is_main": false,
                    "w": 16,
                    "x": 15,
                    "y": 5
                },
                "type": "T",
                "features": {
                    "I": {
                        "colors": true,
                        "likelihood": 0.9
                    },
                    "R": {},
                    "T": {}
                },
                "mouse": {
                    "type": "move",
                    "features": {
                        "point": {
                            "dx": 974,
                            "dy": 243
                        },
                        "button": "left",
                        "amount": 1,
                        "delays_ms": 100,
                        "pixels": 100
                    }
                },
                "keyboard": {
                    "string": "sdgf",
                    "delays_ms": 100,
                    "durations_ms": 100
                }
            }
        ],
        "background": "data:image/png;base64,iVBORwB/AAd0tkvmgB3dAAAAAElFTkSuQmCC"
    }



}
