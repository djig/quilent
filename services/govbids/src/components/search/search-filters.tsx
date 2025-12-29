"use client";

import { useTransition } from "react";
import { X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useSearchFilters } from "@/hooks/use-search";

const SET_ASIDES = [
  { value: "", label: "All Set-Asides" },
  { value: "SBA", label: "Small Business" },
  { value: "8A", label: "8(a)" },
  { value: "HUBZone", label: "HUBZone" },
  { value: "SDVOSB", label: "Service-Disabled Veteran" },
  { value: "WOSB", label: "Women-Owned" },
];

export function SearchFilters() {
  const [filters, setFilters] = useSearchFilters();
  const [isPending, startTransition] = useTransition();

  const hasActiveFilters = filters.agency || filters.naics_code || filters.set_aside;

  const handleClearFilters = () => {
    startTransition(() => {
      setFilters({
        agency: "",
        naics_code: "",
        set_aside: "",
        page: 1,
      });
    });
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium">Filters</h3>
        {hasActiveFilters && (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleClearFilters}
            disabled={isPending}
          >
            <X className="mr-1 h-3 w-3" />
            Clear
          </Button>
        )}
      </div>
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="space-y-2">
          <Label htmlFor="agency">Agency</Label>
          <Input
            id="agency"
            placeholder="e.g., DOD, HHS"
            value={filters.agency}
            onChange={(e) =>
              startTransition(() => {
                setFilters({ agency: e.target.value, page: 1 });
              })
            }
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="naics">NAICS Code</Label>
          <Input
            id="naics"
            placeholder="e.g., 541512"
            value={filters.naics_code}
            onChange={(e) =>
              startTransition(() => {
                setFilters({ naics_code: e.target.value, page: 1 });
              })
            }
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="set-aside">Set-Aside</Label>
          <Select
            value={filters.set_aside}
            onValueChange={(value) =>
              startTransition(() => {
                setFilters({ set_aside: value, page: 1 });
              })
            }
          >
            <SelectTrigger id="set-aside">
              <SelectValue placeholder="All Set-Asides" />
            </SelectTrigger>
            <SelectContent>
              {SET_ASIDES.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  );
}
