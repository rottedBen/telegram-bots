import sys
import os

BASE_PATH = os.environ.get('BASE_PATH')
sys.path.insert(1, BASE_PATH + '/telegram-bots/src')

from libraries.util import create_href_str

url_website = 'boobank.org'
url_uniswap_boo = 'https://app.uniswap.org/#/swap?inputCurrency=BOO'
url_uniswap_ecto = 'https://app.uniswap.org/#/swap?inputCurrency=ECTO'
url_uniswap_pool_boo_eht = 'https://app.uniswap.org/#/add/ETH/BOO'
url_uniswap_pool_boo_ecto = 'https://app.uniswap.org/#/add/boo/ecto'
url_etherscan_boo = 'https://etherscan.io/token/BOO'
url_etherscan_ecto = 'https://etherscan.io/token/ECTO'
url_astrotools_boo = 'https://app.astrotools.io/pair-explorer/BOO'
url_dextools_boo = 'https://www.dextools.io/app/uniswap/pair-explorer/BOO'
url_twitter_boobank = 'https://twitter.com/BooBank'
url_discord_boobank = 'https://discord.gg/cQDTQH7'

links = '<b>Website:</b> ' + create_href_str(url_website, 'boobank.org') + '\n' \
        + '<b>Uniswap:</b> ' + create_href_str(url_uniswap_boo, "$BOOB") + " " + create_href_str(url_uniswap_ecto,
                                                                                                '$ECTO') + '\n' \
        + '<b>Pools:</b> ' + create_href_str(url_uniswap_pool_boo_eht, '$BOOB-$ETH') + ' ' + create_href_str(
    url_uniswap_pool_boo_ecto, '$BOOB-$ECTO') + '\n' \
        + '<b>Etherscan:</b> ' + create_href_str(url_etherscan_boo, '$BOOB') + " " + create_href_str(
    url_etherscan_ecto, '$ECTO') + '\n' \
        + '<b>Charts:</b> ' + create_href_str(url_astrotools_boo, 'Astrotools') + ' ' + create_href_str(
    url_dextools_boo, 'DexTools') + '\n' \
        + '<b>Social medias: </b>' + create_href_str(url_twitter_boobank, 'Twitter') + ' ' + create_href_str(url_discord_boobank, 'Discord') + '\n' \
        + '<b>Telegram groups:</b> @BooBankToken @BooBankNews'

how_to_swap = """Swapping <b>ECTO for ETH:</b>
In order to successfully swap ecto for eth:
- Make sure to increase the slippage to at least 5%
- Keep at least 0.05 ecto for every ecto that you wish to swap in your wallet
- Fast gas is always a plus
Swapping <b>ECTO - BOOB:</b>
- Same, but slippage at 10%"""
