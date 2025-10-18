# 🏡 Home Lab Expose

Expose your home lab services securely to the internet using NoIP DNS and the free Cloudflare tunnel.

---

## 🚀 Overview

**Home Lab Expose** helps you make your self-hosted services accessible from anywhere, using free NoIP DNS. Perfect for hobbyists, developers, and anyone running a home server.

---

## 🛠️ Features

- 🌐 Securely expose local services
- 🔄 NoIP DNS
- 📝 Easy setup and customization

---

## 🔗 Useful Links

- [NoIP](https://www.noip.com/)
    Free, reliable dynamic DNS service.
    Example: `yourdomain.ddns.net`

- [Redirect.Pizza](https://redirect.pizza/)
    Simple, reliable URL redirection service.
    Example: Redirect `yourdomain.ddns.net` to your service.

---

## 💡 Example Use Case

- Host a private wiki at `wiki.yourdomain.ddns.net`
- Expose your home automation dashboard at `home.yourdomain.ddns.net`
- Redirect old URLs to new services using Redirect.Pizza

---


## ⚙️ Configuration

1. **Create a NoIP account and domain**
    - Register at [NoIP](https://www.noip.com/) and create your hostname (e.g., `yourdomain.ddns.net`).
    - Configure your router or device to update the NoIP DNS record, or use the provided scripts.
    - Example DNS configuration: ![NoIP DNS Configuration](img/noip_dns_configuration.png)
        - it could be that NoIP will not let you add the wildcard domain at the first try. add a normal domain and then edit it and add the checkbox at Wildcard.

2. **Configure the service**
    - Edit `config/example_config.yaml` with your NoIP credentials, API keys, and desired domains.
    - Rename `example_config.yaml` to `config.yaml` when ready.
    - Example fields:
      ```yaml
      noip:
         username: "your_noip_username"
         password: "your_noip_password"
         hostname: "yourdomain.ddns.net"
      redirect_pizza:
         api_key: "your_redirect_pizza_api_key"
      exposed_services:
         - name: "wiki"
            port: 8080
            domain: "wiki.yourdomain.ddns.net"
      ```

3. **Networking (Recommended)**
    - Add the container to a dedicated Docker network with only the containers you want to expose.

4. **Start the service**
    - Run with Docker Compose:
      ```bash
      docker compose up
      ```

5. **Scripts and Utilities**
    - See the `env/`, `scripts/`, and `transfer/` folders for helper scripts (e.g., DNS updates, monitoring, transfer management).

6. **Reverse Proxy & Monitoring**
    - Use the tools in `tunnel/` for DNS resolution, monitoring, and redirection.

---
---
