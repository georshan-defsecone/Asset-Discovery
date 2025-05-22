import { useEffect, useState, useRef } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import { Card, CardContent } from "@/components/ui/card";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";

const LabelValue = ({ label, value }: { label: string; value: any }) => {
  if (typeof value === "object" && value !== null && !Array.isArray(value)) {
    return (
      <div className="mb-4">
        <div className="font-bold text-left">{label}:</div>
        <div className="ml-4 mt-1 space-y-2">
          {Object.entries(value).map(([k, v]) => (
            <LabelValue key={k} label={k} value={v} />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="mb-2 flex">
      <span className="w-64 font-semibold text-left">{label}:</span>
      <span className="text-left">{value || "—"}</span>
    </div>
  );
};

const AssetDetail = () => {
  const { asset_name } = useParams<{ asset_name: string }>();
  const [assetDetails, setAssetDetails] = useState<Record<string, any>>({});
  const [hardware, setHardware] = useState<any[]>([]);
  const [software, setSoftware] = useState<any[]>([]);
  const [users, setUsers] = useState<any[]>([]);
  const [security, setSecurity] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState(false);

  const contentRef = useRef<HTMLDivElement>(null);
  const { project_name } = useParams<{  project_name: string }>();

 useEffect(() => {
  axios
    .get(`http://localhost:80/api/project/${project_name}/asset/${asset_name}`)
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
    .get(`http://localhost/api/project/${project_name}/asset/${assetName}/pdf/`, {
      responseType: 'blob',
    })
    .then((response) => {
      const file = new Blob([response.data], { type: 'application/pdf' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(file);
      link.download = `${assetName}_details.pdf`;
      link.click();
    })
    .catch((error) => {
      console.error('Error downloading PDF:', error);
    })
    .finally(() => setDownloading(false));
};


  if (loading) return <div className="p-8">Loading...</div>;
  if (error) return <div className="p-8 text-red-600">{error}</div>;

  return (
    <div className="flex-1 flex flex-col p-8">
      <Card>
        <div className="flex justify-between items-center p-4">
          <h2 className="text-xl font-bold">Asset: {asset_name}</h2>
          <Button onClick={() => {handleDownloadPDF(asset_name)}} disabled={downloading}>
            {downloading ? "Generating PDF..." : "Download PDF"}
          </Button>
        </div>
        <CardContent className="p-6" ref={contentRef}>
          <Tabs defaultValue="assetdetails" className="w-full">
            <TabsList className="flex justify-evenly gap-4 bg-white mb-4">
              <TabsTrigger value="assetdetails">Asset Details</TabsTrigger>
              <TabsTrigger value="hardware">Hardware</TabsTrigger>
              <TabsTrigger value="software">Software</TabsTrigger>
              <TabsTrigger value="users">Users</TabsTrigger>
              <TabsTrigger value="security">Security</TabsTrigger>
            </TabsList>

            <TabsContent value="assetdetails" className="space-y-4">
              {Object.entries(assetDetails).map(([key, value]) => (
                <LabelValue key={key} label={key} value={value} />
              ))}
            </TabsContent>

            <TabsContent value="hardware" className="space-y-6">
              {hardware.map((section, index) => {
                if ("ComputerSystem" in section) {
                  const data = section["ComputerSystem"];
                  return (
                    <div key={`cs-${index}`} className="mt-8">
                      <h3 className="text-lg font-bold mb-2 text-left">ComputerSystem</h3>
                      <div className="ml-4 space-y-2">
                        {Object.entries(data).map(([k, v]) => (
                          <LabelValue key={k} label={k} value={v} />
                        ))}
                      </div>
                    </div>
                  );
                }
                if ("OperatingSystem" in section) {
                  const data = section["OperatingSystem"];
                  return (
                    <div key={`os-${index}`} className="mt-8">
                      <h3 className="text-lg font-bold mb-2 text-left">OperatingSystem</h3>
                      <div className="ml-4 space-y-2">
                        {Object.entries(data).map(([k, v]) => (
                          <LabelValue key={k} label={k} value={v} />
                        ))}
                      </div>
                    </div>
                  );
                }

                const [hardwareType, data] = Object.entries(section)[0];
                if (Array.isArray(data)) {
                  const allKeys = Array.from(new Set(data.flatMap(item => Object.keys(item)))); 
                  return (
                    <div key={index} className="mt-8">
                      <h3 className="text-lg font-bold mb-2 text-left">{hardwareType}</h3>
                      <Table>
                        <TableHeader>
                          <TableRow>
                            {allKeys.map((key) => (
                              <TableHead key={key} className="text-left">{key}</TableHead>
                            ))}
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {data.map((item, rowIndex) => (
                            <TableRow key={rowIndex}>
                              {allKeys.map((key) => (
                                <TableCell key={key} className="text-left">{item[key] ?? "—"}</TableCell>
                              ))}
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  );
                }

                const keys = Object.keys(data);
                const values = Object.values(data);
                return (
                  <div key={index} className="mt-8">
                    <h3 className="text-lg font-bold mb-2 text-left">{hardwareType}</h3>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          {keys.map((key) => (
                            <TableHead key={key} className="text-left">{key}</TableHead>
                          ))}
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        <TableRow>
                          {values.map((value, idx) => (
                            <TableCell key={idx} className="text-left">{value ?? "—"}</TableCell>
                          ))}
                        </TableRow>
                      </TableBody>
                    </Table>
                  </div>
                );
              })}
            </TabsContent>

            <TabsContent value="software" className="space-y-6">
              {software.length === 0 ? (
                <div>No software found.</div>
              ) : (
                (() => {
                  const allKeys = Array.from(new Set(software.flatMap(item => Object.keys(item))));
                  return (
                    <Table>
                      <TableHeader>
                        <TableRow>
                          {allKeys.map((key) => (
                            <TableHead key={key} className="text-left">{key}</TableHead>
                          ))}
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {software.map((item, index) => (
                          <TableRow key={index}>
                            {allKeys.map((key) => (
                              <TableCell key={key} className="text-left">{item[key] ?? "—"}</TableCell>
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
                  const allKeys = Array.from(new Set(users.flatMap(user => Object.keys(user))));
                  return (
                    <Table>
                      <TableHeader>
                        <TableRow>
                          {allKeys.map((key) => (
                            <TableHead key={key} className="text-left">{key}</TableHead>
                          ))}
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {users.map((user, index) => (
                          <TableRow key={index}>
                            {allKeys.map((key) => (
                              <TableCell key={key} className="text-left">{user[key] ?? "—"}</TableCell>
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
                        <h3 className="text-lg font-bold mb-2 text-left">{securityType}</h3>
                        {securityType.toLowerCase().includes("antivirus") ? (
                          <div className="ml-4 space-y-2">
                            {Object.entries(data).map(([k, v]) => (
                              <LabelValue key={k} label={k} value={v} />
                            ))}
                          </div>
                        ) : Array.isArray(data) ? (
                          <Table>
                            <TableHeader>
                              <TableRow>
                                {Object.keys(data[0] || {}).map((key) => (
                                  <TableHead key={key} className="text-left">{key}</TableHead>
                                ))}
                              </TableRow>
                            </TableHeader>
                            <TableBody>
                              {data.map((item, i) => (
                                <TableRow key={i}>
                                  {Object.values(item).map((val, j) => (
                                    <TableCell key={j} className="text-left">{val ?? "—"}</TableCell>
                                  ))}
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        ) : (
                          <Table>
                            <TableHeader>
                              <TableRow>
                                {Object.keys(data).map((key) => (
                                  <TableHead key={key} className="text-left">{key}</TableHead>
                                ))}
                              </TableRow>
                            </TableHeader>
                            <TableBody>
                              <TableRow>
                                {Object.values(data).map((val, j) => (
                                  <TableCell key={j} className="text-left">{val ?? "—"}</TableCell>
                                ))}
                              </TableRow>
                            </TableBody>
                          </Table>
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
    </div>
  );
};

export default AssetDetail;
