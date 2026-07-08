import { createFileRoute } from '@tanstack/react-router'
import PowerBIClient from '../components/PowerBIClient'

export const Route = createFileRoute('/report')({
  component: ReportPage,
})

function ReportPage() {
  return (
    <div style={{ height: '100vh', width: '100vw' }}>
      <PowerBIClient />
    </div>
  )
}