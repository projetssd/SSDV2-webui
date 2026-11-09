import { useEffect, useRef, useState } from 'react'

import { apiFetch } from '@/api/client'
import type { components } from '@/api/schema'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { fr } from '@/i18n/fr'

export function WireguardQr() {
  const [open, setOpen] = useState(false)
  const [png, setPng] = useState<string | null>(null)
  const [error, setError] = useState(false)
  const request = useRef<AbortController | null>(null)

  useEffect(() => () => request.current?.abort(), [])

  async function reveal() {
    request.current?.abort()
    const controller = new AbortController()
    request.current = controller
    setPng(null)
    setError(false)
    setOpen(true)
    try {
      const result = await apiFetch<components['schemas']['PeerQrOut']>('/apps/wireguard/peer-qr', {
        method: 'POST', signal: controller.signal, cache: 'no-store',
      })
      if (!controller.signal.aborted) setPng(result.png_base64)
    } catch {
      if (!controller.signal.aborted) setError(true)
    }
  }

  function close(value: boolean) {
    setOpen(value)
    if (!value) {
      request.current?.abort()
      setPng(null)
      setError(false)
    }
  }

  return (
    <>
      <Button variant="outline" onClick={() => void reveal()}>{fr.wireguardQr.reveal}</Button>
      <Dialog open={open} onOpenChange={close}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{fr.wireguardQr.title}</DialogTitle>
            <DialogDescription>{fr.wireguardQr.description}</DialogDescription>
          </DialogHeader>
          {error ? <p role="alert">{fr.wireguardQr.error}</p> : png ? (
            <img className="mx-auto max-w-full bg-white p-2" src={`data:image/png;base64,${png}`} alt={fr.wireguardQr.title} />
          ) : <p role="status">{fr.common.loading}</p>}
          <Button variant="outline" onClick={() => close(false)}>{fr.common.close}</Button>
        </DialogContent>
      </Dialog>
    </>
  )
}
