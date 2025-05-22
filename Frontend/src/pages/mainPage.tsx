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
    console.log(projectName)
    axios
      .get(`http://127.0.0.1:80/project/${projectName}`)
      .then((response) => {
        setAssets(response.data.devices);
        setLoading(false);
      })
      .catch((error) => {
        setError("Error fetching assets. Please try again.");
        setLoading(false);
      });
  }, [projectName]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div className="w-full h-full inset-0 bg-gray-100 p-8">
      <Card className="w-full mx-auto">
        <CardContent>
          <div className="relative mb-4">
            <h1 className="text-2xl font-bold text-center">
              Devices in {projectName}
            </h1>
          </div>
          <div className="overflow-x-auto">
            <Table className="w-[90%]">
              <TableHeader>
                <TableRow>
                  <TableHead className="w-1/2 text-center">Name</TableHead>
                  <TableHead className="w-1/2 text-center">
                    IP Address
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {assets.map((asset, index) => (
                  <TableRow key={`${asset.name}-${index}`}>
                    <TableCell className="text-center">
                      <Link
                        to={`/projects/${projectName}/assets/${asset.name}`}
                        className="text-blue-600 hover:underline"
                      >
                        {asset.name}
                      </Link>
                    </TableCell>
                    <TableCell className="text-center">
                      {asset.ip_address}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
