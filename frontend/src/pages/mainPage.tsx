import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import axios from "axios";
import { Card, CardContent } from "@/components/ui/card";
import {
  Table,
  TableHeader,
  TableRow,
  TableHead,
  TableBody,
  TableCell,
} from "@/components/ui/table";
import Header from "@/components/ui/header";
import Sidebar from "@/components/ui/sidebar";

interface Asset {
  name: string;
  ip_address: string;
}

export default function MainPage() {
  const { projectName } = useParams<{ projectName: string }>();
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    axios
      .get(`http://127.0.0.1:80/project/${projectName}`)
      .then((response) => {
        setAssets(response.data.devices);
        setLoading(false);
      })
      .catch(() => {
        setError("Error fetching assets. Please try again.");
        setLoading(false);
      });
  }, [projectName]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div className="flex">
      <Sidebar />

      <div className="flex-1 ml-64">
        <Header />

        <main className="p-6 mt-16 min-h-screen bg-gray-100">
          <Card className="w-full mx-auto max-w-4xl ml-18 mt-5">
            <CardContent>
              <h1 className="text-2xl font-bold text-center mb-6">
                Devices in {projectName}
              </h1>

              <div className="overflow-x-auto">
                <Table className="w-full">
                  <TableHeader>
                    <TableRow>
                      <TableHead className="text-left">Name</TableHead>
                      <TableHead className="text-right">IP Address</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {assets.map((asset, index) => (
                      <TableRow key={`${asset.name}-${index}`}>
                        <TableCell className="text-left">
                          <Link
                            to={`/projects/${projectName}/assets/${asset.name}`}
                            className="text-black-600 hover:underline"
                          >
                            {asset.name}
                          </Link>
                        </TableCell>
                        <TableCell className="text-right">
                          {asset.ip_address}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </main>
      </div>
    </div>
  );
}
