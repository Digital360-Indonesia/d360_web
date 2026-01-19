# SSH Connection Timeout Troubleshooting

## Error: `dial tcp ***:***: i/o timeout`

GitHub Actions cannot connect to your VPS via SSH. Follow these steps to fix:

## Step 1: Test SSH from Local Machine

First, verify SSH works from your local machine:

```bash
# Test SSH connection
ssh -i /path/to/your/key digital360@YOUR_SERVER_IP -p PORT

# Example:
ssh -i ~/.ssh/id_rsa digital360@72.61.214.241 -p 22
```

**If this works**: SSH is configured correctly, problem is with firewall/security groups.
**If this fails**: Fix SSH configuration first.

---

## Step 2: Check GitHub Secrets

Verify all required secrets are set in GitHub repository:

1. Go to: `https://github.com/Digital360-Indonesia/digital360v2.1/settings/secrets/actions`
2. Check these secrets exist:

   - **PROD_VPS_HOST** = Your server IP (e.g., `72.61.214.241`)
   - **PROD_VPS_USERNAME** = `digital360`
   - **PROD_VPS_SSH_KEY** = Private SSH key content
   - **PROD_VPS_PORT** = SSH port (default `22` or your custom port)

3. Verify secrets are correct:
   ```bash
   # Check what key you're using locally
   cat ~/.ssh/id_rsa  # or your private key path

   # Compare with PROD_VPS_SSH_KEY in GitHub
   ```

---

## Step 3: Server-Side Fixes

### A. Check SSH Daemon is Running

```bash
# Login to your server (via console or other access)
sudo systemctl status ssh
# or
sudo systemctl status sshd

# If not running:
sudo systemctl start ssh
sudo systemctl enable ssh
```

### B. Check SSH Configuration

```bash
# View SSH config
sudo nano /etc/ssh/sshd_config

# Ensure these settings:
Port 22  # or your custom port
PermitRootLogin no  # or prohibit-password
PasswordAuthentication no  # if using key-based auth
PubkeyAuthentication yes

# Restart SSH after changes
sudo systemctl restart ssh
```

### C. Add SSH Public Key to Server

```bash
# On the server, add GitHub Actions public key:
mkdir -p ~/.ssh
chmod 700 ~/.ssh
nano ~/.ssh/authorized_keys

# Paste the PUBLIC key (not private key) corresponding to PROD_VPS_SSH_KEY
chmod 600 ~/.ssh/authorized_keys
```

---

## Step 4: Firewall Configuration

### Option A: UFW (Ubuntu/Debian)

```bash
# Check UFW status
sudo ufw status

# Allow SSH from specific GitHub Actions IP ranges
sudo ufw allow from 192.30.252.0/22 to any port YOUR_SSH_PORT
sudo ufw allow from 185.199.108.0/22 to any port YOUR_SSH_PORT
sudo ufw allow from 185.199.109.0/22 to any port YOUR_SSH_PORT
sudo ufw allow from 185.199.110.0/22 to any port YOUR_SSH_PORT
sudo ufw allow from 185.199.111.0/22 to any port YOUR_SSH_PORT

# Or allow SSH from anywhere (less secure)
sudo ufw allow YOUR_SSH_PORT/tcp

# Reload firewall
sudo ufw reload
```

### Option B: firewalld (CentOS/RHEL)

```bash
# Check firewalld status
sudo firewall-cmd --state

# Allow SSH port
sudo firewall-cmd --permanent --add-port=22/tcp  # or your custom port
sudo firewall-cmd --reload
```

### Option C: iptables

```bash
# List current rules
sudo iptables -L -n

# Allow SSH
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT  # or your custom port

# Save rules
sudo iptables-save | sudo tee /etc/iptables/rules.v4
```

---

## Step 5: Cloud Provider Security Groups

If your VPS is from a cloud provider, check their firewall:

### DigitalOcean
- Go to Networking > Firewalls
- Add rule: Allow TCP port 22 from All IPv4 (or specific IPs)

### AWS
- Go to EC2 > Security Groups
- Add inbound rule: SSH (22) from 0.0.0.0/0

### Vultr
- Go to Firewall > Add Rule
- Allow TCP port 22 from All IPv4

### Other Providers
- Check "Security Groups", "Firewall Rules", or "Network Security"
- Allow inbound TCP on your SSH port (default 22)

---

## Step 6: Network Connectivity

Check if server is reachable:

```bash
# From your local machine
ping YOUR_SERVER_IP

# Check if port is open
telnet YOUR_SERVER_IP 22
# or
nc -zv YOUR_SERVER_IP 22
```

---

## Step 7: Verify SSH Key Format

Make sure the SSH key in GitHub Secrets is correct:

```bash
# On your local machine, view the private key
cat ~/.ssh/id_rsa

# It should look like:
-----BEGIN OPENSSH PRIVATE KEY-----
... base64 encoded content ...
-----END OPENSSH PRIVATE KEY-----

# OR for old format:
-----BEGIN RSA PRIVATE KEY-----
... base64 encoded content ...
-----END RSA PRIVATE KEY-----

# Copy the ENTIRE content including BEGIN/END lines
```

**Important**: Use the **PRIVATE KEY**, not the public key (.pub file).

---

## Quick Test Command

After making changes, test SSH manually:

```bash
# From your local machine
ssh -i ~/.ssh/your_key digital360@YOUR_SERVER_IP -p 22

# If this works, try GitHub Actions deployment again
```

---

## Common Issues & Solutions

### Issue: "Permission denied (publickey)"
- **Cause**: Wrong SSH key or key not added to server
- **Fix**: Verify PROD_VPS_SSH_KEY matches a key in ~/.ssh/authorized_keys on server

### Issue: "Connection refused"
- **Cause**: SSH not running or wrong port
- **Fix**: Start SSH daemon and verify port in /etc/ssh/sshd_config

### Issue: "Connection timed out"
- **Cause**: Firewall blocking or server unreachable
- **Fix**: Open firewall port or check security group rules

### Issue: "Host key verification failed"
- **Cause**: Server host key changed
- **Fix**: Remove old host key: `ssh-keygen -R YOUR_SERVER_IP`

---

## GitHub Actions IP Ranges

If you want to allow only GitHub Actions IPs:

```
192.30.252.0/22
185.199.108.0/22
185.199.109.0/22
185.199.110.0/22
185.199.111.0/22
```

Or allow from **all IPs** for testing (less secure):
```
0.0.0.0/0
```

---

## Still Not Working?

1. Check GitHub Actions logs for more details
2. Verify server is online: `ping YOUR_SERVER_IP`
3. Check SSH logs on server: `sudo tail -f /var/log/auth.log` (Ubuntu) or `sudo tail -f /var/log/secure` (CentOS)
4. Try deploying manually first to isolate the issue

---

## Last Resort: Manual Deploy Temporarily

If CI/CD is urgent but SSH is problematic, deploy manually:

```bash
# SSH to server
ssh digital360@YOUR_SERVER_IP

# Run deployment
cd /home/digital360/web/digital360.id/public_html
git pull origin main
npm install
npm run build

# Fix permissions
chmod -R 755 dist/
```

Then fix SSH configuration for automated deployment.
