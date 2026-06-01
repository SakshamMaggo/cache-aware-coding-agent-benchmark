Fix the cache-key builder.

It should create a stable key for chat-style prompt messages. The key should ignore volatile fields such as `request_id` and `timestamp`, normalize repeated whitespace inside message content, and avoid mutating the input messages.