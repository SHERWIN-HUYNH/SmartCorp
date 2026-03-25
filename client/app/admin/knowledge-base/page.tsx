import { StatsOverview } from '@/components/admin/knowledge-base/StatsOverview';
import { UploadSection } from '@/components/admin/knowledge-base/UploadSection';
import { ProcessingQueue } from '@/components/admin/knowledge-base/ProcessingQueue';
import { DocumentTable } from '@/components/admin/knowledge-base/DocumentTable';

export default function KnowledgeBase() {
    return (
        <div className="p-8 max-w-7xl mx-auto w-full space-y-8">
          <StatsOverview />
          <UploadSection />
          <ProcessingQueue />
          <DocumentTable />
        </div>
    );

}