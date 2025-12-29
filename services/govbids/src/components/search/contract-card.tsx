"use client";

import Link from "next/link";
import { ExternalLink, Calendar, Building2, Hash } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { Entity } from "@/lib/api";

interface ContractCardProps {
  contract: Entity;
}

export function ContractCard({ contract }: ContractCardProps) {
  const data = contract.data as Record<string, unknown>;
  const agency = (data.agency as string) || "Unknown Agency";
  const naicsCode = data.naics_code as string;
  const setAside = data.set_aside as string;
  const deadline = data.response_deadline as string;

  const formattedDeadline = deadline
    ? new Date(deadline).toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      })
    : null;

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <div className="space-y-1 flex-1">
            <CardTitle className="text-lg leading-tight line-clamp-2">
              <Link
                href={`/search/${contract.id}`}
                className="hover:text-primary transition-colors"
              >
                {contract.title}
              </Link>
            </CardTitle>
            <CardDescription className="flex items-center gap-1">
              <Building2 className="h-3 w-3" />
              {agency}
            </CardDescription>
          </div>
          {contract.source_url && (
            <Button variant="ghost" size="icon" asChild>
              <a
                href={contract.source_url}
                target="_blank"
                rel="noopener noreferrer"
              >
                <ExternalLink className="h-4 w-4" />
                <span className="sr-only">Open in SAM.gov</span>
              </a>
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-2 mb-3">
          {naicsCode && (
            <Badge variant="secondary" className="text-xs">
              <Hash className="mr-1 h-3 w-3" />
              NAICS: {naicsCode}
            </Badge>
          )}
          {setAside && (
            <Badge variant="outline" className="text-xs">
              {setAside}
            </Badge>
          )}
        </div>
        {formattedDeadline && (
          <div className="flex items-center gap-1 text-sm text-muted-foreground">
            <Calendar className="h-3 w-3" />
            <span>Due: {formattedDeadline}</span>
          </div>
        )}
        {contract.summary && (
          <p className="mt-2 text-sm text-muted-foreground line-clamp-2">
            {contract.summary}
          </p>
        )}
      </CardContent>
    </Card>
  );
}
