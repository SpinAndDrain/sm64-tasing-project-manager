import getpass
import argparse
import bot
import secret


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-pw', '--password', type=str)
    args = parser.parse_args()

    key = args.password or getpass.getpass("Please enter the password: ")

    ENV = None
    try:
        ENV = secret.decrypt(key, "global.env.enc")
        if not ENV:
            print("Wrong password")
            return
        ENV = secret.read_env(ENV)
    except FileNotFoundError:
        print(f"[Error] Missing environment variables: File '{file_path}' not found")
        return
    except IOError as e:
        print(f"[Error] While accessing file '{file_path}': ", e)
        return

    bot.setup_bot(ENV).run(ENV["TOKEN"])


if __name__ == "__main__":
    main()