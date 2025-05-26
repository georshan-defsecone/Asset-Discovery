import { useEffect, useState, useRef } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import Header from "@/components/ui/header";
import Sidebar from "@/components/ui/sidebar";

const LabelValue = ({ label, value }: { label: string; value: any }) => {
  if (typeof value === "object" && value !== null && !Array.isArray(value)) {
    return (
      <div className="mb-4">
        <div className="text-left ">{label}</div>
        <div className="ml-0 mt-1 space-y-2">
          {Object.entries(value).map(([k, v]) => (
            <LabelValue key={k} label={k} value={v} />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="mb-2 flex">
      <span className="w-64 text-left">{label}</span>
      <span className="text-left">
        {typeof value === "boolean" ? (value ? "Yes" : "No") : value || "—"}
      </span>
    </div>
  );
};

const AssetDetail = () => {
  const { asset_name } = useParams<{ asset_name: string }>();
  const { project_name } = useParams<{ project_name: string }>();
  const [assetDetails, setAssetDetails] = useState<Record<string, any>>({});
  const [hardware, setHardware] = useState<any[]>([]);
  const [software, setSoftware] = useState<any[]>([]);
  const [users, setUsers] = useState<any[]>([]);
  const [security, setSecurity] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState(false);

  const contentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    axios
      .get(
        `http://localhost:80/api/project/${project_name}/asset/${asset_name}`
      )
      .then((response) => {
        setAssetDetails(response.data.AssetDetails || {});
        setHardware(response.data.Hardware || []);
        setSoftware(response.data.Software || []);
        setUsers(response.data.Users || []);
        setSecurity(response.data.Security || []);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching asset details:", err);
        setError("Failed to fetch asset details.");
        setLoading(false);
      });
  }, [asset_name, project_name]);

  const handleDownloadPDF = (assetName: string) => {
    if (!project_name) return;

    setDownloading(true);
    axios
      .get(
        `http://localhost/api/project/${project_name}/asset/${assetName}/pdf/`,
        {
          responseType: "blob",
        }
      )
      .then((response) => {
        const file = new Blob([response.data], { type: "application/pdf" });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(file);
        link.download = `${assetName}_details.pdf`;
        link.click();
      })
      .catch((error) => {
        console.error("Error downloading PDF:", error);
      })
      .finally(() => setDownloading(false));
  };

  if (loading) return <div className="p-8">Loading...</div>;
  if (error) return <div className="p-8 text-red-600">{error}</div>;

  return (
    <div>
      <Sidebar />

      <div className="ml-64">
        <Header />

        <main className="p-6 mt-16 min-h-screen bg-gray-100">
          <Card className="w-full ml-18 mt-5 shadow-lg">
            <div className="flex justify-between items-center p-4">
              <h2 className="text-xl font-bold">Asset: {asset_name}</h2>
              <Button
                onClick={() => handleDownloadPDF(asset_name)}
                disabled={downloading}
              >
                {downloading ? "Generating PDF..." : "Download PDF"}
              </Button>
            </div>

            <CardContent className="p-6" ref={contentRef}>
              <Tabs defaultValue="assetdetails" className="w-full">
                <TabsList className="flex gap-2 flex-wrap bg-transparent mb-4">
                  {[
                    { label: "Asset Details", value: "assetdetails" },
                    { label: "Hardware", value: "hardware" },
                    { label: "Software", value: "software" },
                    { label: "Users", value: "users" },
                    { label: "Security", value: "security" },
                  ].map((tab) => (
                    <TabsTrigger
                      key={tab.value}
                      value={tab.value}
                      className="px-4 py-2 text-sm font-medium border border-gray-300 rounded-md shadow-sm bg-white text-black hover:bg-gray-100 data-[state=active]:bg-black data-[state=active]:text-white"
                    >
                      {tab.label}
                    </TabsTrigger>
                  ))}
                </TabsList>

                <TabsContent value="assetdetails" className="space-y-4">
                  {assetDetails &&
                    typeof assetDetails === "object" &&
                    Reflect.ownKeys(assetDetails).map((key) => (
                      <LabelValue
                        key={String(key)}
                        label={String(key)}
                        value={assetDetails[key as keyof typeof assetDetails]}
                      />
                    ))}
                </TabsContent>

                <TabsContent value="hardware" className="space-y-6">
                  {hardware.map((item, idx) => {
                    const entries = Object.entries(item);
                    return entries.map(([section, content]) => (
                      <div key={`${idx}-${section}`}>
                        <h3 className="text-lg font-bold mb-2 text-left">
                          {section}
                        </h3>
                        {Array.isArray(content) ? (
                          <Table>
                            <TableHeader>
                              <TableRow>
                                {Object.keys(content[0] || {}).map((key) => (
                                  <TableHead key={key}>{key}</TableHead>
                                ))}
                              </TableRow>
                            </TableHeader>
                            <TableBody>
                              {content.map((row, rowIndex) => (
                                <TableRow key={rowIndex}>
                                  {Object.values(row).map((value, cellIndex) => (
                                    <TableCell key={cellIndex}>
                                      {typeof value === "boolean"
                                        ? value
                                          ? "Yes"
                                          : "No"
                                        : value === null || value === undefined
                                        ? "—"
                                        : typeof value === "object"
                                        ? JSON.stringify(value, null, 2)
                                        : String(value)}
                                    </TableCell>
                                  ))}
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        ) : (
                          <div className=" space-y-2">
                            {Object.entries(content).map(([k, v]) => (
                              <LabelValue key={k} label={k} value={v} />
                            ))}
                          </div>
                        )}
                      </div>
                    ));
                  })}
                </TabsContent>

                <TabsContent value="software" className="space-y-6">
                  {software.length === 0 ? (
                    <div>No software found.</div>
                  ) : (
                    (() => {
                      const allKeys = Array.from(
                        new Set(software.flatMap((item) => Object.keys(item)))
                      );
                      return (
                        <Table>
                          <TableHeader>
                            <TableRow>
                              {allKeys.map((key) => (
                                <TableHead key={key} className="text-left">
                                  {key}
                                </TableHead>
                              ))}
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {software.map((item, index) => (
                              <TableRow key={index}>
                                {allKeys.map((key) => (
                                  <TableCell key={key} className="text-left">
                                    {item[key] ?? "—"}
                                  </TableCell>
                                ))}
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      );
                    })()
                  )}
                </TabsContent>

                <TabsContent value="users" className="space-y-6">
                  {users.length === 0 ? (
                    <div>No users found.</div>
                  ) : (
                    (() => {
                      const allKeys = Array.from(
                        new Set(users.flatMap((user) => Object.keys(user)))
                      );
                      return (
                        <Table>
                          <TableHeader>
                            <TableRow>
                              {allKeys.map((key) => (
                                <TableHead key={key} className="text-left">
                                  {key}
                                </TableHead>
                              ))}
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {users.map((user, index) => (
                              <TableRow key={index}>
                                {allKeys.map((key) => (
                                  <TableCell key={key} className="text-left">
                                    {typeof user[key] === "boolean"
                                      ? user[key]
                                        ? "Yes"
                                        : "No"
                                      : user[key] ?? "—"}
                                  </TableCell>
                                ))}
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      );
                    })()
                  )}
                </TabsContent>

                <TabsContent value="security" className="space-y-6">
                  {security.length === 0 ? (
                    <div>No security data found.</div>
                  ) : (
                    security.map((section, index) => (
                      <div key={index} className="space-y-4 mt-8">
                        {Object.entries(section).map(([securityType, data]) => (
                          <div key={securityType}>
                            <h3 className="text-lg font-bold mb-2 text-left">
                              {securityType}
                            </h3>
                            {Array.isArray(data) ? (
                              <Table>
                                <TableHeader>
                                  <TableRow>
                                    {Object.keys(data[0] || {}).map((key) => (
                                      <TableHead key={key} className="text-left">
                                        {key}
                                      </TableHead>
                                    ))}
                                  </TableRow>
                                </TableHeader>
                                <TableBody>
                                  {data.map((item, i) => (
                                    <TableRow key={i}>
                                      {Object.values(item).map((val, j) => (
                                        <TableCell key={j} className="text-left">
                                          {typeof val === "boolean"
                                            ? val
                                              ? "Yes"
                                              : "No"
                                            : val ?? "—"}
                                        </TableCell>
                                      ))}
                                    </TableRow>
                                  ))}
                                </TableBody>
                              </Table>
                            ) : typeof data === "object" ? (
                              <div className=" space-y-2">
                                {Object.entries(data).map(([k, v]) => (
                                  <LabelValue key={k} label={k} value={v} />
                                ))}
                              </div>
                            ) : (
                              <p>{String(data)}</p>
                            )}
                          </div>
                        ))}
                      </div>
                    ))
                  )}
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </main>
      </div>
    </div>
  );
};

export default AssetDetail;
