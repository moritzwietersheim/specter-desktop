# Frequently Asked Questions

## ABOUT THE PROJECT

The goal of this project is to make a convenient and user-friendly GUI around Bitcoin Core with a focus on multisignature setup with airgapped (offline) hardware wallets. 

We first wanted to make a new hardware wallet (HWW), but when we understood that everything can be hacked, we decided to build a user-friendly Multisig Desktop App and nice DIY Hardware Wallet.

**Why is that good for Bitcoin?**

 - User: Better Security with multisig setup 
 - User: Better Privacy with own node 
 - HWW Makers: More HW wallets sold 
 - Node Makers: More Nodes sold 
 - Network: More nodes running 

With this user-friendly multisig & node setup we can actually incentivize the Bitcoin hodler to run his own node to protect his privacy and improve his security! 

## *Why the name Specter?*

    "A specter is haunting the modern world, the specter of crypto anarchy."
    The Crypto Anarchist Manifesto - Timothy C. May - Sun, 22 Nov 92 12:11:24 PST
    
Specter is that little ghost helping the sovereign cypherpunk to protect his property rights.
We are aware of the vulnerability [Spectre](https://en.wikipedia.org/wiki/Spectre_(security_vulnerability) and know there is an infinite game against vulnerabilities.

In Bitcoin Cold storage we can use multisig setups and different hardware wallets to mitigate these risks, while protecting our privacy by verifying transactions on our own node.

## GENERAL QUESTIONS

## *How safe is the app to use?*

It is watch-only (private keys are protected by HWWs) and compatible with multisig in Electrum, so even if something breaks you always have a fallback option while we fix the bug. So go for it :)

We try to use default descriptors and derivation paths exactly for this reason - to be compatible with other wallets. Would be nice to keep it this way, but at a certain point we will need to diverge - for example when we add miniscript support.

At the moment we don't try to be very backward-compatible. At some point we may change wallet storage format for example, and you would need to migrate using some script or create wallets from scratch. In this case, we would provide migration scripts.

## *What's the difference between Specter-Desktop and Specter-DIY?*

Specter-Desktop is a watch-only GUI software wallet running on Bitcoin Core using its wallet and full node functionality.
Bitcoin Core tracks addresses, UTXO (unspent transaction outputs) and composes PSBT (partially-signed bitcoin transactions).

Whereas, [Specter-DIY](https://github.com/cryptoadvance/specter-diy) is a do-it-yourself hardware wallet from off the shelf components, that signs and broadcasts transactions using QR codes.

## *Do I have to use the Bitcoin-Core wallet functionality? If so, is it considered secure?*

With Specter-Desktop private keys are not used on Bitcoin Core node. 
In order to use watch-only wallets in Bitcoin Core, you need to insert `disablewallet=0` in your `bitcoin.conf` file.

## *What is the practical difference of using PSBT (partially signed bitcoin transaction) with multisig vs. just signing the raw multisig transaction?*

From a user point of view it gives you the ability to store the transaction temporarily before it is signed.

## USAGE

## *How do I run the app?*

After following [these steps](https://github.com/cryptoadvance/specter-desktop#how-to-run) 
You should be able to view it in a browser at: 127.0.0.1:25441/
If not, see [Troubleshoot](https://github.com/cryptoadvance/specter-desktop/new/master/docs#troubleshoot)

## *What do I need to do in order to create a multisig wallet?*

First you need to “add devices” that store public keys for the wallet. After creating the devices, you have to choose the type of wallet you want (2-of-2, 3-of-5, etc.) and select the corresponding devices - you need at least two devices setup in order to create a multisig wallet.

## *Can I use Bluewallet with Specter DIY?*

Yes you can use BlueWallet in watch-only mode and sign with Specter DIY. See it in action [here](https://twitter.com/StepanSnigirev/status/1209426608949465088)

## *Which HWW's are supported?*

Any HWW with HWI, including USB HWW's (Coldcard, Trezor, Ledger, KeepKey etc.)

## *Can this also work with external nodes like Raspiblitz, Nodl, MyNode and Casa?* 

Absolutely, as well as any other DIY bitcoin full, or pruned, node!

Currently [Raspiblitz](https://github.com/rootzoll/raspiblitz) has explicit support and you can automatically install it as bonus-software.

## *Can I use Tor?*

Yes, there is a way to access Specter-Desktop over Tor from outside, here is the [doc](https://github.com/cryptoadvance/specter-desktop/blob/master/docs/tor.md)

With that being said, beware that it's not practical yet to sign transactions via Tor:

 - Specter-DIY needs the camera which is not available in the Tor-browser (yet)
 - You could use HWI-wallets, but you would need to plug the wallet into the machine where Specter-Desktop is running on. However this is usually not the use-case you're looking for when using Tor.

## *How to set the URL for the block explorer?*

This feature is optional and not needed for the wallet to function. 
It's only used for convenience in order to generate URLs for addresses.
Technically, you can use any block explorer but that's not what you want to do, unless you want to try out the feature.
Simply fill in https://blockstream.info/ to use that block explorer, but you will leak privacy doing that.

## BACKING UP FUNDS 

## *If something happens to the `~/.specter` folder, is it still possible to **restore** acccess to multisigs created there (assuming there is no backup of the `~/.specter` folder)?* 

Please make sure you backup your `~/.specter` folder. Specter-Desktop uses a standard multisig. So you can recreate it as soon as you have the **master public keys of ALL the devices** - either with Specter-Desktop or Electrum.

If your `~/.specter` folder is gone and only one of your devices is lost without a backup, then all your funds are **LOST**, even if you have a 1/4-multisig-wallet.

When using Specter and importing an old wallet you would need to rescan blockchain in the wallet settings page.

# TROUBLESHOOT

## *How to upgrade?*

Use this command: `pip3 install cryptoadvance.specter --upgrade`
To check (before and/or afterwards) your installed version, you can use the command: `pip3 show cryptoadvance.specter`

## *How can I access the web interface if it's hosted on a headless computer?* 

You can either set --host 0.0.0.0 `python -m cryptoadvance.specter server --host 0.0.0.0` or configure nginx to forward connections from specific port to specter.
 
Alternatively, you can also define --port 80 if you want to have it on default http port of the computer.

One drawback though is that with http and **external access** you will not get camera scanning functionality. It is an issue if you are using specter-DIY as it's necessary to scan QR codes with signed transactions. To fix that you will need a self-signed certificate, we have a document on that [here](https://github.com/cryptoadvance/specter-desktop/blob/master/docs/self-signed-certificates.md)

## *Keep getting: No matching distribution found for cryptoadvance.specter

Try `pip3 install cryptoadvance.specter`

Specter only works with python3, so use pip3 to install it
`brew install python3`

## *Even after upgrading to python3 it's still looking at 2.7 version. I uninstalled 2.7, so not sure where to go next?*

Run it with the command `python3 -m cryptoadvance.specter server` - then it will use python3

## *How to delete a wallet using a remote full node?*

You can't delete the wallet if you are using remote Bitcoin Core node - there is no RPC call to do it remotely. So, deleting wallet works only on the same computer. 
You can also just delete the wallet manually. It's a folder in `~/.bitcoin` directory and in `~/.specter` as well.

## DIY TROUBLESHOOT

## *Does anyone have any tips on mounting the power bank and QR code scanner to the STM32 board in a somewhat ergonomic manner?*

Use the smallest powerbank possible.

## HWW TROUBLESHOOT

Got stuck for a second because I wasn't safely removing my SD card reader, so the files were 0 bytes.

## *With achow's HWI tool, input and output PSBT are the same. And with Electrum 4, I get a rawtransaction, not a base64 PSBT.*

I solved my issue, it turns out my PSBT needed bip32 hints (whatever that means) included. I can now open lightning channels straight from hardware wallet!

# TECHNICAL QUESTIONS (not dev related)

## *Does specter-desktop require `txindex=1` to be set in your `bitcoin.conf`?*

No, but you need to enable wallets! `disablewallet=0`

# FUTURE FEATURES

## *Will Specter-Desktop ever be a full Hot-Wallet?*

Right now it’s only with external wallets, but there is an open issue for hot wallet.

We have plans to add new device type "this computer", see this [issue](https://github.com/cryptoadvance/specter-desktop/issues/58)

At the moment it is more like a coordinator app. For signing we have [specter-diy](https://github.com/cryptoadvance/specter-diy)

*Comment: Still open for discussion!*

## *How are you guys planning to do airgapped firmware updates via QR codes?*

We haven't tested it yet. We will work on the bootloader soon and try different update mechanisms. QR codes is one of them. Also considering SD card - might be easier as firmware is 1Mb, so it would require 1000 QR codes.

## *Will this device be Shamir Secret Shares compatible?*

Yes it will be, and especially effective in "forget after turn off" mode. Then one could use it to split a secret for wallets that don't support it.

## *Will there be coinjoin support in the future?*

When coinjoin servers and hardware wallets support proof of ownership: https://github.com/satoshilabs/slips/blob/slips-19-20-coinjoin-proofs/slip-0019.md

# VIDEOS

## **1** [Getting started with Specter-DIY and Specter-Desktop](https://twitter.com/CryptoAdvance/status/1235151027348926464)

How to flash and set up an airgapped hardware wallet that uses QR codes to communicate with the host.

In the video: 

 - Flashing the firmware
 - Generating a new key 
 - Importing keys to Specter-Desktop software 
 - Using single-key wallets 
 - Creating a multisignature wallet and importing it to the device 
 - Signing multisig transactions 

## **2** [Assembling Specter-DIY](https://www.youtube.com/watch?v=1H7FqG_FmCw)

Specter-DIY hardware wallet: 

 - off-the-shelf components
 - costs 100$ - assemble in 5 minutes 
 - no soldering 
 - forgets your private key when powered off 

## **3** [Specter-DIY air-gapped open source bitcoin hardware wallet overview](https://twitter.com/KeithMukai/status/1189565099259944961)

## **4** [Build your own bitcoin hardware-wallet YT series](https://www.youtube.com/playlist?list=PLn2qRQUAAg0z_-R0swVuSsNS9bzRu6oP5&app=desktop)

## *What is the difference between the project "diybitcoinhardware.com" & Specter-DIY? Is DIYbitcoinhardware sort of a prerequisite for Specter-DIY?*

Specter-DIY is built on top of that micropython build. DIYbitcoinhardware is focusing more on the toolbox without actual application logic, Specter implements logic and GUI on top of it. 

Yes, that's why the video was recorded - to give some introduction about the tools we use, and hardware wallets logic in general.
