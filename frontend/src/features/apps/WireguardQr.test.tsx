import { act, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { WireguardQr } from '@/features/apps/WireguardQr'

afterEach(() => vi.unstubAllGlobals())

describe('WireguardQr', () => {
  it('fetches only on request and forgets the QR on close', async () => {
    const user = userEvent.setup()
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({
      app: 'wireguard', peer: '1', png_base64: 'private-test-qr',
    }), { headers: { 'content-type': 'application/json' } }))
    vi.stubGlobal('fetch', fetchMock)
    render(<WireguardQr />)
    expect(fetchMock).not.toHaveBeenCalled()
    await user.click(screen.getByRole('button', { name: 'Afficher le QR code' }))
    const image = await screen.findByRole('img')
    expect(image).toHaveAttribute('src', 'data:image/png;base64,private-test-qr')
    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('/apps/wireguard/peer-qr'),
      expect.objectContaining({ method: 'POST', cache: 'no-store' }))
    await user.click(screen.getByRole('button', { name: 'Fermer' }))
    await waitFor(() => expect(screen.queryByRole('img')).not.toBeInTheDocument())
    expect(document.body.innerHTML).not.toContain('private-test-qr')
  })

  it('discards a response arriving after the dialog closes', async () => {
    const user = userEvent.setup()
    let resolve!: (value: Response) => void
    const fetchMock = vi.fn().mockReturnValue(new Promise<Response>((r) => { resolve = r }))
    vi.stubGlobal('fetch', fetchMock)
    render(<WireguardQr />)
    await user.click(screen.getByRole('button', { name: 'Afficher le QR code' }))
    await user.click(screen.getByRole('button', { name: 'Fermer' }))
    await act(async () => resolve(new Response(JSON.stringify({ png_base64: 'late-secret' }))))
    expect(document.body.innerHTML).not.toContain('late-secret')
    expect(fetchMock.mock.calls[0][1].signal.aborted).toBe(true)
  })

  it('shows a generic error without subprocess content', async () => {
    const user = userEvent.setup()
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('private-error-content')))
    render(<WireguardQr />)
    await user.click(screen.getByRole('button', { name: 'Afficher le QR code' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('QR code indisponible')
    expect(document.body.innerHTML).not.toContain('private-error-content')
  })
})
