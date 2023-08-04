from pubq.rest import REST

# Usage example:
if __name__ == "__main__":
    application_id = "your_application_id"
    application_key = "your_application_key"
    application_secret = "your_application_secret"

    rest = REST(application_id, application_key, application_secret)

    channel = "test_channel"
    data = "Hello!"
    result = rest.publish(channel, data)
    print(result)
