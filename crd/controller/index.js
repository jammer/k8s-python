const k8s = require('@kubernetes/client-node')
const mustache = require('mustache')
const request = require('request')
const JSONStream = require('json-stream')
const fs = require('fs').promises

// Use Kubernetes client to interact with Kubernetes

const timeouts = {}

const kc = new k8s.KubeConfig();

process.env.NODE_ENV === 'development' ? kc.loadFromDefault() : kc.loadFromCluster()

const opts = {}
kc.applyToRequest(opts)

const client = kc.makeApiClient(k8s.CoreV1Api);

const sendRequestToApi = async (api, method = 'get', options = {}) => new Promise((resolve, reject) => request[method](`${kc.getCurrentCluster().server}${api}`, {...opts, ...options, headers: { ...options.headers, ...opts.headers }}, (err, res) => err ? reject(err) : resolve(JSON.parse(res.body))))

const fieldsFromDummysite = (object) => ({
  name: object.metadata.name,
  namespace: object.metadata.namespace,
  website: object.spec.website_url
})

const getJobYAML = async (fields) => {
  const deploymentTemplate = await fs.readFile("job.mustache", "utf-8")
  return mustache.render(deploymentTemplate, fields)
}

const jobForDummysiteAlreadyExists = async (fields) => {
  const { name, namespace } = fields
  const { items } = await sendRequestToApi(`/apis/batch/v1/namespaces/${namespace}/jobs`)

  return items.find(item => item.metadata.labels.dummysite === name)
}

const createJob = async (fields) => {
  console.log('Scheduling new job for', fields.name, 'to namespace', fields.namespace)

  const yaml = await getJobYAML(fields)

  return sendRequestToApi(`/apis/batch/v1/namespaces/${fields.namespace}/jobs`, 'post', {
    headers: {
      'Content-Type': 'application/yaml'
    },
    body: yaml
  })
}


const maintainStatus = async () => {
  (await client.listPodForAllNamespaces()).body // A bug in the client(?) was fixed by sending a request and not caring about response

  /**
   * Watch Countdowns
   */

  const dummysite_stream = new JSONStream()

  dummysite_stream.on('data', async ({ type, object }) => {
    const fields = fieldsFromDummysite(object)

    if (type === 'ADDED') {
      //if (await jobForDummysiteAlreadyExists(fields)) return // Restarting application would create new 0th jobs without this check
      createJob(fields)
    }
    //if (type === 'DELETED') cleanupForCountdown(fields)
  })

  request.get(`${kc.getCurrentCluster().server}/apis/stable.dwk/v1/dummysites?watch=true`, opts).pipe(dummysite_stream)

  /**
   * Watch Jobs
   */
/*
  const job_stream = new JSONStream()

  job_stream.on('data', async ({ type, object }) => {
    if (!object.metadata.labels.dummysite) return // If it's not countdown job don't handle
    if (type === 'DELETED' || object.metadata.deletionTimestamp) return // Do not handle deleted jobs
    if (!object?.status?.succeeded) return

    rescheduleJob(object)
  })

  request.get(`${kc.getCurrentCluster().server}/apis/batch/v1/jobs?watch=true`, opts).pipe(job_stream)
  */
}

maintainStatus()
