
# Json format

```json
{
    "1234567890": {                             // user id: {all the things they control}
        "category_id": "1257866829788086312",   
        "channels": {
            "public": {                         // name of the channel and it's attributes
                "id": "1257866831012560926",
                "type": "public",
                "reactions": true,
                "comments": true
            },
            "private": {
                "id": "1257866832166125628",
                "type": "private",
                "member_ids": [
                    "505897723174846466",
                    "681998181340545081"
                ],
                "reactions": true,
                "comments": true
            }
        }
    },
    "505897723174846466": {
        "category_id": "1257866865846386789",
        "channels": {
            "test": {
                "id": "1257866866685378582",
                "type": "public",
                "reactions": true,
                "comments": true
            }
        }
    }
}
```