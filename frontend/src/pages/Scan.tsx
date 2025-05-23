import React, { useState } from "react";
import axios from "axios";
import Header from "@/components/ui/header"; // Adjust path as needed
import Sidebar from "@/components/ui/sidebar";// Adjust path as needed

const Scan: React.FC = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [projectName, setProjectName] = useState("");
  const [domainName, setDomainName] = useState("");
  const [ipAddress, setIpAddress] = useState("");
  const [serverIp, setServerIp] = useState("");
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState<"success" | "error" | "">("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (
      !username.trim() ||
      !password.trim() ||
      !projectName.trim() ||
      !ipAddress.trim() ||
      !serverIp.trim()
    ) {
      setMessage("Please fill in all required fields.");
      setMessageType("error");
      return;
    }

    try {
      const params = new URLSearchParams();
      params.append("username", username);
      params.append("password", password);
      params.append("project_name", projectName);
      params.append("domain", domainName);
      params.append("ip_input", ipAddress);
      params.append("serverip", serverIp);

      const response = await axios.post("http://127.0.0.1:80/start_scan", params, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });

      if (response.status === 200) {
        setMessage(response.data.message || "Scan started successfully.");
        setMessageType("success");
      } else {
        setMessage("Failed to start scan.");
        setMessageType("error");
      }
    } catch (error: any) {
      if (error.response && error.response.data && error.response.data.message) {
        setMessage(error.response.data.message);
      } else {
        setMessage("Error connecting to the server.");
      }
      setMessageType("error");
    }
  };

  return (
    <div className="bg-gray-100 min-h-screen">
      <Header />
      <Sidebar />
      <main className="ml-64 pt-20 px-6 flex items-center justify-center min-h-screen">
        <div className="w-full max-w-md bg-white p-8 rounded-xl shadow-2xl">
          <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">
            Asset Discovery
          </h2>
          <form onSubmit={handleSubmit}>
            <input
              type="text"
              name="username"
              placeholder="Username *"
              autoComplete="off"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full border-b border-gray-400 bg-transparent px-2 py-2 focus:outline-none focus:border-blue-500 text-sm mb-4"
              required
            />
            <input
              type="password"
              name="password"
              placeholder="Password *"
              autoComplete="off"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border-b border-gray-400 bg-transparent px-2 py-2 focus:outline-none focus:border-blue-500 text-sm mb-4"
              required
            />
            <input
              type="text"
              name="project"
              placeholder="Project Name *"
              autoComplete="off"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              className="w-full border-b border-gray-400 bg-transparent px-2 py-2 focus:outline-none focus:border-blue-500 text-sm mb-4"
              required
            />
            <input
              type="text"
              name="domain"
              placeholder="Domain Name"
              autoComplete="off"
              value={domainName}
              onChange={(e) => setDomainName(e.target.value)}
              className="w-full border-b border-gray-400 bg-transparent px-2 py-2 focus:outline-none focus:border-blue-500 text-sm mb-4"
            />
            <input
              type="text"
              name="ip"
              placeholder="IP Address *"
              autoComplete="off"
              value={ipAddress}
              onChange={(e) => setIpAddress(e.target.value)}
              className="w-full border-b border-gray-400 bg-transparent px-2 py-2 focus:outline-none focus:border-blue-500 text-sm mb-4"
              required
            />
            <input
              type="text"
              name="server_ip"
              placeholder="Server IP *"
              autoComplete="off"
              value={serverIp}
              onChange={(e) => setServerIp(e.target.value)}
              className="w-full border-b border-gray-400 bg-transparent px-2 py-2 focus:outline-none focus:border-blue-500 text-sm mb-4"
              required
            />

            <button
              type="submit"
              className="w-full bg-neutral-800 text-white py-2 rounded-md hover:bg-gray-600 transition text-sm"
            >
              Scan
            </button>

            {message && (
              <div
                className={`mt-4 text-center text-sm px-4 py-2 rounded-md transition-all duration-300 ${
                  messageType === "success"
                    ? "bg-green-100 text-green-800 border border-green-300"
                    : "bg-red-100 text-red-800 border border-red-300"
                }`}
              >
                {message}
              </div>
            )}
          </form>
        </div>
      </main>
    </div>
  );
};

export default Scan;
