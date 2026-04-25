import asyncio
from bleak import BleakClient

ADDRESS = "8E6AA1FA-3B99-4A4D-BC3E-ADFB34EC55D6"
CHAR_UUID = "abcd1234-ab12-ab12-ab12-abcdef123456"

async def main():
    print("Connecting to", ADDRESS)

    async with BleakClient(ADDRESS) as client:
        print("Connected:", client.is_connected)

        first_read = True
        last_value = None

        while True:
            value = await client.read_gatt_char(CHAR_UUID)
            text = value.decode("utf-8")

            if first_read:
                print("Initial value ignored:", text)
                first_read = False
                last_value = text
                await asyncio.sleep(0.05)
                continue

            if text != last_value:
                print("New value:", text)
                last_value = text

            await asyncio.sleep(0.05)

asyncio.run(main())
