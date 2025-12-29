import { notFound } from "next/navigation";
import Link from "next/link";
import { auth } from "@/lib/auth";
import { getEntity } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ArrowLeft,
  ExternalLink,
  Calendar,
  Building2,
  Hash,
  MapPin,
  DollarSign,
} from "lucide-react";
import { SaveButton } from "./save-button";

interface ContractDetailPageProps {
  params: Promise<{ id: string }>;
}

export default async function ContractDetailPage({
  params,
}: ContractDetailPageProps) {
  const resolvedParams = await params;
  const session = await auth();

  let contract;
  try {
    contract = await getEntity(resolvedParams.id, session?.accessToken);
  } catch {
    notFound();
  }

  const data = contract.data as Record<string, unknown>;
  const agency = (data.agency as string) || "Unknown Agency";
  const naicsCode = data.naics_code as string;
  const setAside = data.set_aside as string;
  const deadline = data.response_deadline as string;
  const description = data.description as string;
  const placeOfPerformance = data.place_of_performance as string;
  const estimatedValue = data.estimated_value as number;
  const contactInfo = data.contact_info as Record<string, unknown>;
  const solicitationNumber = data.solicitation_number as string;

  const formattedDeadline = deadline
    ? new Date(deadline).toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      })
    : null;

  const formattedValue = estimatedValue
    ? new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        maximumFractionDigits: 0,
      }).format(estimatedValue)
    : null;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="sm" asChild>
          <Link href="/search">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Search
          </Link>
        </Button>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        <div className="flex-1 space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-start justify-between gap-4">
                <div className="space-y-1">
                  <CardTitle className="text-2xl">{contract.title}</CardTitle>
                  <CardDescription className="flex items-center gap-1">
                    <Building2 className="h-4 w-4" />
                    {agency}
                  </CardDescription>
                </div>
                <div className="flex gap-2">
                  <SaveButton
                    contractId={contract.id}
                    accessToken={session?.accessToken}
                  />
                  {contract.source_url && (
                    <Button variant="outline" asChild>
                      <a
                        href={contract.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <ExternalLink className="h-4 w-4 mr-2" />
                        View on SAM.gov
                      </a>
                    </Button>
                  )}
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex flex-wrap gap-2">
                {naicsCode && (
                  <Badge variant="secondary">
                    <Hash className="mr-1 h-3 w-3" />
                    NAICS: {naicsCode}
                  </Badge>
                )}
                {setAside && <Badge variant="outline">{setAside}</Badge>}
                {solicitationNumber && (
                  <Badge variant="secondary">
                    Sol#: {solicitationNumber}
                  </Badge>
                )}
              </div>

              {contract.summary && (
                <div>
                  <h3 className="font-semibold mb-2">AI Summary</h3>
                  <p className="text-muted-foreground">{contract.summary}</p>
                </div>
              )}

              {description && (
                <div>
                  <h3 className="font-semibold mb-2">Description</h3>
                  <p className="text-muted-foreground whitespace-pre-wrap">
                    {description}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="lg:w-80 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Contract Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {formattedDeadline && (
                <div className="flex items-start gap-3">
                  <Calendar className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="font-medium text-sm">Response Deadline</p>
                    <p className="text-sm text-muted-foreground">
                      {formattedDeadline}
                    </p>
                  </div>
                </div>
              )}

              {formattedValue && (
                <div className="flex items-start gap-3">
                  <DollarSign className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="font-medium text-sm">Estimated Value</p>
                    <p className="text-sm text-muted-foreground">
                      {formattedValue}
                    </p>
                  </div>
                </div>
              )}

              {placeOfPerformance && (
                <div className="flex items-start gap-3">
                  <MapPin className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="font-medium text-sm">Place of Performance</p>
                    <p className="text-sm text-muted-foreground">
                      {placeOfPerformance}
                    </p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {contactInfo && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Contact Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                {typeof contactInfo.name === "string" && contactInfo.name && (
                  <p>
                    <span className="font-medium">Name:</span>{" "}
                    {contactInfo.name}
                  </p>
                )}
                {typeof contactInfo.email === "string" && contactInfo.email && (
                  <p>
                    <span className="font-medium">Email:</span>{" "}
                    <a
                      href={`mailto:${contactInfo.email}`}
                      className="text-primary hover:underline"
                    >
                      {contactInfo.email}
                    </a>
                  </p>
                )}
                {typeof contactInfo.phone === "string" && contactInfo.phone && (
                  <p>
                    <span className="font-medium">Phone:</span>{" "}
                    {contactInfo.phone}
                  </p>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
